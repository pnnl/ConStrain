"""
### Description

Section 9.4.1.1.h Automatic full OFF control
- All lighting in the space, including lighting connected to emergency circuits,shall be automatically shut off within 20 minutes of all occupants leaving the space. A control device meeting this requirement shall control no more than 5000 ft2.
- Exceptions:
  - The following lighting is not required to be automatically shut off:
    1. Lighting required for 24/7 continuous operation.
    2. Lighting in spaces where patient care is rendered.
    3. General lighting and task lighting in spaces where automatic shutoff would endanger the safety or security of the room or building occupants.
    4. Lighting load not exceeding 0.02 W/ft2 multiplied by the gross lighted floor area of the building.

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
if area_lit >= 5000:
    fail  # Exceeds maximum area per control device

# Check shutoff timing and power
time_since_occupancy = current_time - last_occupancy_time

if number_occupants < occupancy_threshold and time_since_occupancy > 20_minutes:
    if power_light_total / area_lit <= 0.02:
        pass  # Proper shutoff or within exemption
    else:
        fail  # Lights still on above exemption threshold
else:
    untested  # Cannot verify without vacancy period
```

### Data requirements

- number_occupants: Occupancy count
  - Data Value Unit: count
  - Data Point Affiliation: Zone occupancy

- power_light_total: Lighting power
  - Data Value Unit: power
  - Data Point Affiliation: Lighting system

- area_lit: Floor area
  - Data Value Unit: area
  - Data Point Affiliation: Space configuration

"""

from constrain.checklib import RuleCheckBase


class InteriorLightingControlAutomaticFullOff(RuleCheckBase):
    points = [
        "number_occupants",
        "power_light_total",
        "area_lit",
    ]
    min_lighting_power_density = 0
    last_reported_occupancy = None

    def automatic_full_off(self, data):
        # initialization
        if self.last_reported_occupancy is None:
            self.last_reported_occupancy = data.name

        # verification based on lighted space
        if data["area_lit"] >= 5000:
            return False

        # verification based on power
        date_diff = data.name - self.last_reported_occupancy
        if (
            data["number_occupants"] < self.get_tolerance("ratio", "occupancy")
        ) and date_diff.total_seconds() / 60 > 20:
            if (data["power_light_total"] / data["area_lit"]) <= 0.02:
                check = True
            else:
                check = False
        else:
            check = "Untested"

        # update last identified occupancy flag if applicable
        if data["number_occupants"] >= self.get_tolerance("ratio", "occupancy"):
            self.last_reported_occupancy = data.name
        return check

    def verify(self):
        self.min_lighting_power_density = (
            self.df["power_light_total"].min() / self.df["area_lit"]
        )
        self.result = self.df.apply(lambda d: self.automatic_full_off(d), axis=1)
