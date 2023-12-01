from constrain.checklib import RuleCheckBase
import pandas as pd


class GuestRoomControlTemp(RuleCheckBase):
    points = ["T_z_hea_set", "T_z_coo_set", "O_sch", "tol_occ", "tol_temp"]

    def verify(self):
        tol_occ = self.df["tol_occ"][0]
        tol_temp = self.df["tol_temp"][0]
        year_info = 2000
        result_repo = []
        for idx, day in self.df.groupby(self.df.index.date):
            if (
                day.index.month[0] == 2 and day.index.day[0] == 29
            ):  # skip leap year, although E+ doesn't have leap year the date for loop assumes so because 24:00 time step so, it's intentionally skipped here
                pass
            elif (
                year_info != day.index.year[0]
            ):  # remove the Jan 1st of next year reason: the pandas date for loop iterates one more loop is hour is 24:00:00
                pass
            else:
                if (
                    day["O_sch"] <= tol_occ
                ).all():  # confirmed this room is NOT rented out
                    if (day["T_z_hea_set"] < 15.6 + tol_temp).all() and (
                        day["T_z_coo_set"] > 26.7 - tol_temp
                    ).all():
                        result_repo.append(
                            1
                        )  # pass, confirmed zone temperature setpoint reset during the unrented period
                    else:
                        result_repo.append(
                            0
                        )  # fail, zone temperature setpoint was not reset correctly
                else:  # room is rented out
                    T_z_hea_occ_set = day.query("O_sch > 0.0")["T_z_hea_set"].max()
                    T_z_coo_occ_set = day.query("O_sch > 0.0")["T_z_coo_set"].min()

                    if (
                        day["T_z_hea_set"] < T_z_hea_occ_set - 2.22 + tol_temp
                    ).all() or (
                        day["T_z_coo_set"] > T_z_coo_occ_set + 2.22 - tol_temp
                    ).all():
                        result_repo.append(
                            1
                        )  # pass, confirm the HVAC setpoint control resets when guest room reset when occupants leave the room
                    else:
                        result_repo.append(
                            0
                        )  # fail, reset does not meet the standard or no reset was observed.
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
