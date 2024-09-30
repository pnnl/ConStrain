"""
ASHRAE 90.1-2022 
### Description

Section 9.4.1.4.e Occupancy-sensing light reduction control

- Occupancy-sensing light reduction control: Lighting shall be controlled to automatically reduce the connected lighting power by a minimum of 50% when no activity has been detected in the area illuminated by the controlled luminaires for a time of no longer than 15 minutes. No more than 1500 W of lighting power shall be controlled together.

Verification Item:

- Check if the lighting power is reduced when no occupancy is detected.

### Verification logic

```
design_total_lighting_power = max(total_lighting_power)

date_diff = current_date - last_reported_occupancy # in min
If o < tol_o and date_diff > 15
    If total_lighting_power <= 0.5 * design_total_lighting_power
        Pass
    Else
        Fail
    Endif
Else
    Untested
Endif
```

### Data requirements
- o: number of occupants sensed in the zones served by the system.
- total_lighting_power: reported total lighting power (not the design total lighting power)
- tol_o: occupancy threshold; below that value the zones are considered unoccupied.

"""

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
