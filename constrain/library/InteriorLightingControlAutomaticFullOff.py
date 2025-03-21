"""
ASHRAE 90.1-2022
### Description

Section 9.4.1.1.h Automatic full OFF control

- All lighting in the space, including lighting connected to emergency circuits,shall be automatically shut off within 20 minutes of all occupants leaving the space. A control device meeting this requirement shall control no more than 5000 ft2.
- Exceptions:
  - The following lighting is not required to be automatically shut off:
    1. Lighting required for 24/7 continuous operation.
    2. Lighting in spaces where patient care is rendered.
    3. General lighting and task lighting in spaces where automatic shutoff would endanger the safety or security of the room or building occupants.
    4. Lighting load not exceeding 0.02 W/ft2 multiplied by the gross lighted floor area of the building.

Verification Item:

- Check if the lighting power is reduced when no occupancy is detected.

### Verification logic

```
If lighted_floor_area >= 5000:
    return False

date_diff = current_date - last_reported_occupancy # in min
If o < tol_o and date_diff > 20
    If total_lighting_power / lighted_floor_area <= 0.02
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
- lighted_floor_area: area lit by the device/system considered
- tol_o: occupancy threshold; below that value the zones are considered unoccupied.

"""

from constrain.checklib import RuleCheckBase


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
            check = "Untested"

        # update last identified occupancy flag if applicable
        if data["o"] >= data["tol_o"]:
            self.last_reported_occupancy = data.name
        return check

    def verify(self):
        self.min_lighting_power_density = (
            self.df["total_lighting_power"].min() / self.df["lighted_floor_area"]
        )
        self.result = self.df.apply(lambda d: self.daylight_off(d), axis=1)
