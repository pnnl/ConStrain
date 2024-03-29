from constrain.checklib import RuleCheckBase
import numpy as np


class InteriorLightingControlAutomaticFullOff(RuleCheckBase):
    points = [
        "o",
        "total_lighting_power",
        "lighted_floor_area",
        "tol_o",
    ]
    min_lighting_power_density = 0
    last_reported_occupancy = None

    def daylight_off(self, data):
        # initialization
        if self.last_reported_occupancy is None:
            self.last_reported_occupancy = data.name

        # verification based on lighted space
        if data["lighted_floor_area"] >= 5000:
            return False

        # verification based on power
        date_diff = data.name - self.last_reported_occupancy
        if (data["o"] < data["tol_o"]) and date_diff.total_seconds() / 60 > 20:
            if (data["total_lighting_power"] / data["lighted_floor_area"]) <= 0.02:
                check = True
            else:
                check = False
        else:
            check = np.nan

        # update last identified occupancy flag if applicable
        if data["o"] >= data["tol_o"]:
            self.last_reported_occupancy = data.name
        return check

    def verify(self):
        self.min_lighting_power_density = (
            self.df["total_lighting_power"].min() / self.df["lighted_floor_area"]
        )
        self.result = self.df.apply(lambda d: self.daylight_off(d), axis=1)
