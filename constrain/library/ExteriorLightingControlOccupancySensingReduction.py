from constrain.checklib import RuleCheckBase
import numpy as np


class ExteriorLightingControlOccupancySensingReduction(RuleCheckBase):
    points = [
        "o",
        "total_lighting_power",
        "tol_o",
    ]
    last_reported_occupancy = None
    design_total_lighting_power = None

    def occupancy_sensing_reduction(self, data):
        if self.last_reported_occupancy is None:
            self.last_reported_occupancy = data.name
        date_diff = data.name - self.last_reported_occupancy
        if (data["o"] < data["tol_o"]) and date_diff.total_seconds() / 60 > 15:
            # No activity detected or time since last activity exceeds 15 minutes
            # Therefore, the control requirement is met if the total lighting power is already reduced by at least 50%
            if data["total_lighting_power"] <= 0.5 * self.design_total_lighting_power:
                check = True
            else:
                check = False
        else:
            check = np.nan  # untested

        if data["o"] >= data["tol_o"]:
            self.last_reported_occupancy = data.name
        return check

    def verify(self):
        self.design_total_lighting_power = self.df["total_lighting_power"].max()
        if self.design_total_lighting_power >= 1500:
            self.df["result"] = False
            self.result = self.df["result"]
        else:
            self.result = self.df.apply(
                lambda d: self.occupancy_sensing_reduction(d), axis=1
            )
