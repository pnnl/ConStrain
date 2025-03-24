"""
### Description

This verification aims to check if the return air damper operates correctly in systems with return fan direct building pressure control. The damper position should respond appropriately to heating/cooling modes while allowing the return fan to maintain building pressure through speed control.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Return Air Damper Control with Return Fan Direct Building Pressure

### Verification Approach

The verification checks return air damper position under three conditions:
1. During heating: damper should be at maximum position
2. During cooling: damper should be fully closed
3. Otherwise: damper should modulate between minimum and maximum positions

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with return fans using direct building pressure control
- Climate Zone(s): any
- Component(s): return air dampers, return fans, building pressure sensors

### Verification Algorithm Pseudo Code

```python
if out_htg > 0:
    if abs(pos_damper_ra - pos_damper_ra_max) < tol_pos_damper_ra:
        pass
    else:
        fail
elif out_clg > 0:
    if abs(pos_damper_ra - 0) < tol_pos_damper_ra:
        pass
    else:
        fail
elif 0 < pos_damper_ra < pos_damper_ra_max:
    pass
else:
    fail
```

### Data requirements

- out_htg: Heating output
  - Data Value Unit: percent (0-100)
  - Data point Description: Heating output
  - Data Point Affiliation: System control

- out_clg: Cooling output
  - Data Value Unit: percent (0-100)
  - Data point Description: Cooling output
  - Data Point Affiliation: System control

- pos_damper_ra: Return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Return air damper position
  - Data Point Affiliation: Air handling unit

- pos_damper_ra_max: Maximum return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum return air damper position
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_ra: Return air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Return air damper position tolerance
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReturnFanDirectBuildingPressure(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "ra_p",
        "max_ra_p",
        "ra_p_tol",
    ]

    def return_air_damper(self, data):
        if data["heating_output"] > 0:
            if abs(data["ra_p"] - data["max_ra_p"]) < data["ra_p_tol"]:
                return True
            else:
                return False
        elif data["cooling_output"] > 0:
            if data["ra_p"] < data["ra_p_tol"]:
                return True
            else:
                return False
        elif 0 < data["ra_p"] < data["max_ra_p"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.return_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
