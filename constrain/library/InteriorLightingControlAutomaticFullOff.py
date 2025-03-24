"""
### Description

This verification aims to check if interior lighting systems automatically turn off when spaces are unoccupied. The system should shut off all non-exempt lighting within 20 minutes of occupants leaving, while respecting area limitations and exceptions.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2022
- Code Section: 9.4.1.1 Interior Lighting Controls
- Code Subsection: 9.4.1.1.h Automatic Full OFF Control

### Verification Approach

The verification checks three main criteria:
1. Control area limitation: Each device must control ≤ 5000 ft²
2. Shutoff timing: Lights must turn off within 20 minutes of vacancy
3. Power density exceptions: Allows minimal lighting (≤ 0.02 W/ft²) to remain on

Exceptions not verified:
- 24/7 operation areas
- Patient care spaces
- Safety/security critical areas

### Verification Applicability

- Building Type(s): any except healthcare
- Space Type(s): all except safety-critical
- System(s): interior lighting
- Climate Zone(s): any
- Component(s): occupancy sensors, lighting controls

### Verification Algorithm Pseudo Code

```python
# Check control area limitation
if area_floor_lit >= 5000:
    fail  # Exceeds maximum area per control device

# Check shutoff timing and power
time_since_occupancy = current_time - last_occupancy_time

if occupancy < occupancy_threshold and time_since_occupancy > 20_minutes:
    if p_light_total / area_floor_lit <= 0.02:
        pass  # Proper shutoff or within exemption
    else:
        fail  # Lights still on above exemption threshold
else:
    untested  # Cannot verify without vacancy period
```

### Data requirements

- n_occ: Occupancy count
  - Data Value Unit: count
  - Data point Description: Number of occupants
  - Data Point Affiliation: Zone occupancy

- p_light_total: Lighting power
  - Data Value Unit: power
  - Data point Description: Total lighting power
  - Data Point Affiliation: Lighting system

- area_floor_lit: Floor area
  - Data Value Unit: area
  - Data point Description: Lighted floor area
  - Data Point Affiliation: Space configuration

- tol_n_occ: Occupancy threshold
  - Data Value Unit: count
  - Data point Description: Occupancy tolerance
  - Data Point Affiliation: Zone occupancy

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
