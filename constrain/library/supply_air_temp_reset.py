from datetime import date

import matplotlib.pyplot as plt
import seaborn as sns
from constrain.checklib import RuleCheckBase


class SupplyAirTempReset(RuleCheckBase):
    points = ["T_sa_sp", "T_z_cool"]

    def verify(self):
        t_sa_sp_max = max(self.df["T_sa_sp"])
        t_sa_sp_min = min(self.df["T_sa_sp"])

        self.result = (t_sa_sp_max - t_sa_sp_min) >= (
            self.df["T_z_cool"] - t_sa_sp_min
        ) * 0.25 * 0.99  # 0.99 being the numeric threshold

    def plot(self, plot_option, fig_size=(6.4, 4.8), plt_pts=None):
        print(
            "Specific plot method implemented, additional distribution plot is being added!"
        )
        sns.histplot(self.df["T_sa_sp"])
        plt.title("All samples distribution of T_sa_sp")
        plt.savefig(f"{self.results_folder}/All_samples_distribution_of_T_sa_sp.png")

        super().plot(plot_option, plt_pts, fig_size)

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(date(2000, 1, 1), date(2001, 1, 1)):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df.loc[daystr]
            day = self.result[daystr]
            if daydf["T_sa_sp"].max() - daydf["T_sa_sp"].min() > 0:
                return day, daydf
            return day, daydf
