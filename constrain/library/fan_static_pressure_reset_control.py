from constrain.checklib import RuleCheckBase


class FanStaticPressureResetControl(RuleCheckBase):
    points = [
        "p_set",
        "d_VAV_1",
        "d_VAV_2",
        "d_VAV_3",
        "d_VAV_4",
        "d_VAV_5",
    ]

    def verify(self):
        d_vav_points = ["d_VAV_1", "d_VAV_2", "d_VAV_3", "d_VAV_4", "d_VAV_5"]
        d_vav_df = self.df[d_vav_points]

        for row_num, (index, row) in enumerate(self.df.iterrows()):
            if row_num != 0:
                if (d_vav_df.loc[index] > 0.9).any():
                    self.df.at[index, "result"] = "Untested"
                else:
                    if self.df.at[index, "p_set"] < self.df.at[prev_index, "p_set"]:
                        self.df.at[index, "result"] = True
                    else:
                        self.df.at[index, "result"] = False
            else:
                self.df.at[index, "result"] = "Untested"
            prev_index = index

        self.result = self.df["result"]
