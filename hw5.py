import math
import pathlib
from pathlib import Path
from typing import Tuple, Union
import pandas as pd
import pytest
import json
import numpy as np
from matplotlib import pyplot as plt 


class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """

    def __init__(self, data_fname: Union[pathlib.Path, str]):
        self._verify_fname(data_fname)  # raises exception if bad fname
        self.data_fname = Path(str(data_fname))
        self.data = None
            
    def __str__(self) -> str:
        return f"QuestionnaireAnalysis: fname='{self.data_fname}', data={self.data}"

    def _verify_fname(self, data_fname):
        """ Verify the filename"""        
        data_fname = Path(str(data_fname))
        if not data_fname.exists():
            raise ValueError("the file does not exist")

    def read_data(self):
        """Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        self.data = pd.read_json(self.data_fname)

    # region Q1
    def show_age_distrib(self) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates and plots the age distribution of the participants.
        Returns
        -------
        hist : np.ndarray
        Number of people in a given bin
        bins : np.ndarray
        Bin edges
        """
        ages = []
        for participant_i in self.data.to_dict('records'):
            age = participant_i["age"]
            if not np.isnan(age):
                ages.append(age)
        hist, bins, _ = plt.hist(ages, bins=[0,10,20,30,40,50,60,70,80,90,100])
        plt.show()
        return hist, bins
    # endregion

    # region Q2
    def validate_mail(self, email):
        """
        Contains exactly one "@" sign, but doesn't start or end with it.
        Contains a "." sign, but doesn't start or end with it.
        The letter following the "@" sign (i.e, appears after it) must not be ".".
        """
        return email.count("@") == 1 \
            and "." in email \
            and email[0] != "@" \
            and email[0] != "." \
            and email[-1] != "@" \
            and email[-1] != "." \
            and email[email.find("@") + 1] != "."


    def remove_rows_without_mail(self) -> pd.DataFrame:
        """Checks self.data for rows with invalid emails, and removes them.
        
        Returns
        -------
        df : pd.DataFrame
        A corrected DataFrame, i.e. the same table but with the erroneous rows removed and
        the (ordinal) index after a reset.
        """
        records = self.data.to_dict('records')
        filtered = [participant for participant in records if self.validate_mail(participant["email"])]
        df = pd.DataFrame(data=filtered)
        return df
    # endregion

    # region Q3
    def fill_na_with_mean(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Finds, in the original DataFrame, the subjects that didn't answer
        all questions, and replaces that missing value with the mean of the
        other grades for that student.

        Returns
        -------
        df : pd.DataFrame
            The corrected DataFrame after insertion of the mean grade
        arr : np.ndarray
            Row indices of the students that their new grades were generated
        """
        cols = ['q1', 'q2', 'q3', 'q4', 'q5']
        df = self.data
        df_q = df[cols]

        s = df_q.isna().any(axis=1)
        s = s.index[s]
        arr = s.to_numpy()

        df_q = df_q.fillna(df_q.mean())
        df =pd.concat([df.drop(columns=cols), df_q], axis = 1)
        return df, arr
    # endregion

    # region Q4
    def score_subjects(self, maximal_nans_per_sub: int = 1) -> pd.DataFrame:
        """Calculates the average score of a subject and adds a new "score" column
        with it.

        If the subject has more than "maximal_nans_per_sub" NaN in his grades, the
        score should be NA. Otherwise, the score is simply the mean of the other grades.
        The datatype of score is UInt8, and the floating point raw numbers should be
        rounded down.

        Parameters
        ----------
        maximal_nans_per_sub : int, optional
            Number of allowed NaNs per subject before giving a NA score.

        Returns
        -------
        pd.DataFrame
            A new DF with a new column - "score".
        """
        cols = ['q1', 'q2', 'q3', 'q4', 'q5']
        nans = [i for i, row in self.data[cols].iterrows() if len(cols) - row.count() > maximal_nans_per_sub]   # row indices containing >maximal_nans_per_sub NaNs
        score = [math.floor(row.mean()) for _, row in self.data[cols].iterrows()]   # means of all rows
        for i in nans:
            score[i] = pd.NA
        score = pd.Series(score, name="score", dtype=pd.UInt8Dtype())
        df = pd.concat([self.data, score], axis=1)
        return df
    # endregion

    # region Q5
    def correlate_gender_age(self) -> pd.DataFrame:
        """Looks for a correlation between the gender of the subject, their age
        and the score for all five questions.
    
        Returns
        -------
        pd.DataFrame
            A DataFrame with a MultiIndex containing the gender and whether the subject is above
            40 years of age, and the average score in each of the five questions.
        """
        df = self.data
        df = df[df['age'].notnull()]
        s = df['age']
        s = s.where(s > 40, False)
        s = s.where(s == False, True)
        df = df.assign(age=s)
        df.set_index(['gender', 'age'], append=True)
        return df.groupby(['gender', 'age']).mean()[['q1','q2','q3','q4','q5']]
    # endregion



if __name__ == '__main__':
    filepath = r"data.json"
    a = QuestionnaireAnalysis(data_fname=filepath)
    a.read_data()
    print("\nQuestion 1")
    print(a.show_age_distrib())
    print("\nQuestion 2")
    print(a.remove_rows_without_mail())
    print("\nQuestion 3")
    print(a.fill_na_with_mean())
    print("\nQuestion 4")
    print(a.score_subjects())
    print("\nQuestion 5")
    print(a.correlate_gender_age())
