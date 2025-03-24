"""
### Description

This verification aims to check if the outdoor air damper operates correctly in systems with return fan direct building pressure control. The damper should maintain a position that supports proper building pressurization control.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Outdoor Air Damper Control with Return Fan Direct Building Pressure

### Verification Approach

The verification checks that the outdoor air damper maintains its maximum position within an acceptable tolerance. This position allows the return fan to directly control building pressure through its speed modulation.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with return fans using direct building pressure control
- Climate Zone(s): any
- Component(s): outdoor air dampers, return fans, building pressure sensors

### Verification Algorithm Pseudo Code

```python
if abs(pos_damper_oa - pos_damper_oa_max) < tol_pos_damper_oa:
    pass
else:
    fail
```

### Data requirements

- pos_damper_oa: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Outdoor air damper position
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_max: Maximum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum outdoor air damper position
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_oa: Outdoor air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper position tolerance
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure(RuleCheckBase):
    points = [
        "oa_p",
        "max_oa_p",
        "oa_p_tol",
    ]

    def outdoor_air_damper(self, data):
        if abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.outdoor_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
