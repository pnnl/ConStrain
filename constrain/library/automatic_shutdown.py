from constrain.checklib import RuleCheckBase
import pandas as pd


class AutomaticShutdown(RuleCheckBase):
    points = ["hvac_set"]

    def verify(self):
        copied_df = (
            self.df.copy()
        )  # copied not to store unnecessary intermediate variables in self.df dataframe
        copied_df.reset_index(
            inplace=True
        )  # convert index column back to normal column
        copied_df = copied_df.rename(
            columns={"index": "Date"}
        )  # rename the index column to Date
        copied_df["hvac_set_diff"] = copied_df[
            "hvac_set"
        ].diff()  # calculate the difference between previous and current rows
        copied_df = copied_df.dropna(axis=0)  # drop NaN row
        copied_df = copied_df.loc[
            copied_df["hvac_set_diff"] != 0.0
        ]  # filter out 0.0 values
        copied_df["Date"] = pd.to_datetime(
            copied_df["Date"], format="%Y-%m-%d %H:%M:%S"
        )
        df2 = copied_df.groupby(pd.to_datetime(copied_df["Date"]).dt.date).apply(
            lambda x: x.iloc[[0, -1]]
        )  # group by start/end time

        copied_df["start_time"] = df2["hvac_set_diff"].iloc[::2]  # even number row
        copied_df["end_time"] = df2["hvac_set_diff"].iloc[1::2]  # odd number row

        copied_df["min_start_time"] = copied_df.query("start_time == 1")[
            "Date"
        ].dt.hour.min()
        copied_df["max_start_time"] = copied_df.query("start_time == 1")[
            "Date"
        ].dt.hour.max()
        copied_df["min_end_time"] = copied_df.query("end_time == -1")[
            "Date"
        ].dt.hour.min()
        copied_df["max_end_time"] = copied_df.query("end_time == -1")[
            "Date"
        ].dt.hour.max()

        self.result = (copied_df["min_start_time"] != copied_df["max_start_time"]) & (
            copied_df["min_end_time"] != copied_df["max_end_time"]
        )
