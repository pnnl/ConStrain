"""
### Description

Section 5.16.2.3
- Supply air temperature shall be controlled to setpoint using a control loop whose output is mapped to sequence the heating coil (if applicable), outdoor air damper, return air damper, and cooling coil.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
- Code Subsection: 5.16.2.3 Outdoor Air Damper Control with Return Fan Direct Building Pressure

### Verification Approach

This verification aims to check if the outdoor air damper operates correctly in systems with return fan direct building pressure control. The damper should maintain a position that supports proper building pressurization control.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with return fans using direct building pressure control
- Climate Zone(s): any
- Component(s): outdoor air dampers, return fans, building pressure sensors

### Verification Algorithm Pseudo Code

```python
if abs(position_damper_air_outdoor - position_damper_air_outdoor_max) = 0:
    pass
else:
    fail
```

### Data requirements

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor_max: Maximum outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure(RuleCheckBase):
    points = [
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_max",
    ]

    def outdoor_air_damper(self, data):
        if abs(
            data["position_damper_air_outdoor"]
            - data["position_damper_air_outdoor_max"]
        ) < self.get_tolerance("damper", "command"):
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
