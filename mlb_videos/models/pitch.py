import os
import pandas as pd
from tqdm import tqdm

from analysis.ump_calls import calculate_miss
from utils import rank_dict_list

class Pitch:
    def __init__(self, d):
        """Sets attributes of Pitch Class
        Based on dictionary passed
        """
        for k, v in d.items():
            setattr(self, k, v)

    def get_metadata(self):
        """
        """
        return self.__dict__

    def get_metadata_fields(self):
        """
        """
        return list(self.__dict__.keys())

    def add_fields(self,d):
        """
        """
        for k,v in d.items():
            if k in self.get_metadata_fields():
                continue
            else:
                setattr(self, k, v)


class Pitches:
    def __init__(self,df):
        """
        """
        self.df = df
        self.pitch_objs = []
        self.pitch_ct = len(df)
        self._generate_pitches()

    def _generate_pitches(self):
        """
        """
        for _, row in self.df.iterrows():
            self.pitch_objs.append(Pitch(row.to_dict()))

    def _get_pitch(self, pitch_id):
        """
        """
        return [x for x in self.pitch_objs if x.pitch_id == pitch_id][0]

    def _update_pitch_attrs(self, dl):
        """
        """
        for d in dl:
            p = self._get_pitch(d['pitch_id'])
            p.add_fields(d)

    def calculate_missed_calls(self):
        """
        """
        for p in tqdm(self.pitch_objs, total=len(self.pitch_objs)):
            calculate_miss(p)

    def rank_pitches(self, partition_by: list = [], order_by: list = [],
                    ascending: bool = False, name: str = None):
        """
        """
        cols = ['pitch_id'] + partition_by + order_by
        rnked = rank_dict_list(
            dl = [{k:v for k, v in d.items() if k in cols} for d in self.get_pitch_dict()],
            order_by = order_by,
            asc = ascending,
            partition_by = partition_by,
            name = name
        )
        if name:
            self._update_pitch_attrs(
                [{k:v for k, v in d.items() if k in ['pitch_id',name]} for d in rnked]
            )

    def get_pitch_dict(self) -> list:
        """
        """
        return [x.get_metadata() for x in self.pitch_objs]

    def get_pitch_objs(self) -> list:
        """
        """
        return self.pitch_objs

    def get_pitch_df(self) -> pd.DataFrame:
        """
        """
        return pd.DataFrame(self.get_pitch_dict())

