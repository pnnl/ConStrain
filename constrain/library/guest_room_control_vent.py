from constrain.checklib import CheckLibBase
import pandas as pd


class GuestRoomControlVent(CheckLibBase):
    points = [
        "m_z_oa",
        "O_sch",
        "area_z",
        "height_z",
        "v_outdoor_per_zone",
        "tol_occ",
        "tol_oa_flow",
    ]

    def verify(self):
        tol_occ = self.df["tol_occ"][0]
        tol_m = self.df["tol_oa_flow"][0]
        zone_volume = self.df["area_z"][0] * self.df["height_z"][0]
        m_z_oa_set = self.df["v_outdoor_per_zone"][0] * self.df["area_z"][0]

        year_info = 2000
        result_repo = []
        for idx, day in self.df.groupby(self.df.index.date):
            if day.index.month[0] == 2 and day.index.day[0] == 29:
                pass
            elif year_info != day.index.year[0]:
                pass
            else:
                if (
                    day["O_sch"] <= tol_occ
                ).all():  # confirmed this room is NOT rented out
                    if (day["m_z_oa"] == 0).all():
                        result_repo.append(1)  # pass,
                    else:
                        result_repo.append(0)  # fail
                else:  # room is rented out
                    if (day["m_z_oa"] > 0).all():
                        if (
                            day["m_z_oa"] == m_z_oa_set
                            or day["m_z_oa"].sum(axis=1) == zone_volume
                        ):
                            result_repo.append(1)  # pass
                        else:
                            result_repo.append(0)  # fail
                    else:
                        result_repo.append(0)
                year_info = day.index.year[0]

        dti = pd.date_range("2020-01-01", periods=365, freq="D")
        self.result = pd.Series(result_repo, index=dti)

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
