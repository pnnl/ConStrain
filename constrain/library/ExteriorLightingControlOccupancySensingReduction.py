"""
### Description

This verification aims to check if exterior lighting control operates correctly based on occupancy sensing. The system should automatically reduce lighting power when no activity is detected in the illuminated area.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2022
- Code Section: 9.4.1.4 Exterior Lighting Control
- Code Subsection: 9.4.1.4.e Occupancy-sensing light reduction control

### Verification Approach

The verification checks that when no activity is detected for more than 15 minutes, the lighting power is reduced by at least 50% of the maximum observed power. Additionally, it verifies that no more than 1500W of lighting power is controlled together.

### Verification Applicability

- Building Type(s): any
- Space Type(s): exterior spaces
- System(s): exterior lighting systems
- Climate Zone(s): any
- Component(s): lighting controls, occupancy sensors

### Verification Algorithm Pseudo Code

```
design_lighting_power = max(p_power_light_total)

# First check maximum power limit
if design_lighting_power >= 1500:
    return False

# Then check power reduction on no occupancy
date_diff = current_date - last_reported_occupancy # in min
if n_occupants < tol_occupants and date_diff > 15:
    if p_power_light_total <= 0.5 * design_lighting_power:
        return True
    else:
        return False
else:
    return "Untested"
```

### Data requirements

- n_occupants: Number of occupants
  - Data Value Unit: count
  - Data point Description: Number of occupants
  - Data Point Affiliation: Zone occupancy

- p_power_light_total: Lighting power
  - Data Value Unit: power
  - Data point Description: Total lighting power
  - Data Point Affiliation: Lighting system

- tol_occupants: Occupancy threshold
  - Data Value Unit: count
  - Data point Description: Occupancy tolerance
  - Data Point Affiliation: Zone occupancy

"""

from constrain.checklib import RuleCheckBase


class ExteriorLightingControlOccupancySensingReduction(RuleCheckBase):
    points = [
        "number_occupants",
        "power_light_total",
    ]
    last_reported_occupancy = None
    design_lighting_power = None

    def occupancy_sensing_reduction(self, data):
        if self.last_reported_occupancy is None:
            self.last_reported_occupancy = data.name
        date_diff = data.name - self.last_reported_occupancy
        if (
            data["number_occupants"] < self.get_tolerance("ratio", "occupancy")
        ) and date_diff.total_seconds() / 60 > 15:
            # No activity detected or time since last activity exceeds 15 minutes
            # Therefore, the control requirement is met if the total lighting power is already reduced by at least 50%
            if data["power_light_total"] <= 0.5 * self.design_lighting_power:
                check = True
            else:
                check = False
        else:
            check = "Untested"

        if data["number_occupants"] >= self.get_tolerance("ratio", "occupancy"):
            self.last_reported_occupancy = data.name
        return check

    def verify(self):
        self.design_lighting_power = self.df["power_light_total"].max()
        if self.design_lighting_power >= 1500:
            self.df["result"] = False
            self.result = self.df["result"]
        else:
            self.result = self.df.apply(
                lambda d: self.occupancy_sensing_reduction(d), axis=1
            )
