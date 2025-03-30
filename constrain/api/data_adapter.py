"""
data_adapter.py
====================================
Data Adapter API
"""

import sys, os, logging, datetime, copy
import pandas as pd

sys.path.append("..")
from constrain.datetimeep import *


class DataAdapter:

    @staticmethod
    def digest_long_csv(
        data_path: str,
        time_col: str,
        point_name_assembly: list,
        value_col: str,
        point_name_assembly_delim: str = "_",
        interpolate=False,  # reserved for later implementation
        interpolate_interval_min=None,  # reserved for later implementation
    ) -> pd.DataFrame:

        if not os.path.isfile(data_path):
            logging.error(f"The file {data_path} does not exists.")
            return None

        data = pd.read_csv(data_path)

        data["_temp_point_name"] = data.apply(
            lambda row: point_name_assembly_delim.join(
                [row[col] for col in point_name_assembly]
            ),
            axis=1,
        )

        data_new = data[[time_col, "_temp_point_name", value_col]]

        data_new_wide = data_new.pivot_table(
            index=time_col,
            columns="_temp_point_name",
            values=value_col,
            aggfunc="first",  # this is to deal with duplicate time stamp for a specific data point in the data. we just pick the value of first apperance
        )

        return data_new_wide
