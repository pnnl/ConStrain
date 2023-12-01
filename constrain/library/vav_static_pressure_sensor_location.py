from constrain.checklib import RuleCheckBase
from datetime import date


class VAVStaticPressureSensorLocation(RuleCheckBase):
    points = ["p_fan_set", "tol_P_fan"]

    def verify(self):
        self.result = self.df["p_fan_set"] < 298.608 + self.df["tol_P_fan"]

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
