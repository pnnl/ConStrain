from constrain.checklib import RuleCheckBase
from datetime import date


class FanStaticPressureResetControl(RuleCheckBase):
    points = [
        "p_set",
        "p_set_min",
        "d_VAV_1",
        "d_VAV_2",
        "d_VAV_3",
        "d_VAV_4",
        "d_VAV_5",
        "tol",
    ]

    def verify(self):
        d_vav_points = ["d_VAV_1", "d_VAV_2", "d_VAV_3", "d_VAV_4", "d_VAV_5"]
        d_vav_df = self.df[d_vav_points]
        self.df["result"] = True

        for row_num, (index, row) in enumerate(self.df.iterrows()):
            if row_num != 0:
                if (d_vav_df.loc[index] > 0.9).any():
                    self.df.at[index, "result"] = True
                else:
                    if self.df.at[index, "p_set"] > self.df.at[index, "p_set_min"]:
                        if (
                            self.df.at[index, "p_set"]
                            < self.df.at[prev_index, "p_set"] + self.df.at[index, "tol"]
                        ):
                            self.df.at[index, "result"] = True
                        else:
                            self.df.at[index, "result"] = False
                    else:
                        self.df.at[index, "result"] = True
            prev_index = index

        self.result = self.df["result"]

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(
            date(self.df.index[0].year, self.df.index[0].month, self.df.index[0].day),
            date(
                self.df.index[-1].year, self.df.index[-1].month, self.df.index[-1].day
            ),
        ):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df.loc[daystr]
            day = self.result[daystr]

            return day, daydf

    def all_plot_aio(self, plt_pts):
        pass

    def all_plot_obo(self, plt_pts):
        pass

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
