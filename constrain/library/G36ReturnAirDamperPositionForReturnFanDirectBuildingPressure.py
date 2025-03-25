"""
### Description

This verification aims to check if the return air damper operates correctly in systems with return fan direct building pressure control. The damper position should respond appropriately to heating/cooling modes while allowing the return fan to maintain building pressure through speed control.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
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
if q_heat > 0:
    if abs(pos_damper_ra - pos_damper_ra_max) < tol_pos_damper_ra:
        pass
    else:
        fail
elif q_cool > 0:
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

- q_heat: Heating signal
  - Data Value Unit: percent
  - Data point Description: Heating signal (0-100)
  - Data Point Affiliation: System control

- q_cool: Cooling signal
  - Data Value Unit: percent
  - Data point Description: Cooling signal (0-100)
  - Data Point Affiliation: System control

- pos_damper_ra: Return air damper command
  - Data Value Unit: percent
  - Data point Description: Return air damper command
  - Data Point Affiliation: Air handling unit

- pos_damper_ra_max: Maximum return air damper command
  - Data Value Unit: percent
  - Data point Description: Maximum return air damper command
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_ra: Return air damper command tolerance
  - Data Value Unit: percent
  - Data point Description: Return air damper command tolerance
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReturnFanDirectBuildingPressure(RuleCheckBase):
    points = [
        "q_heat",
        "q_cool",
        "pos_damper_ra",
        "pos_damper_ra_max",
        "tol_pos_damper_ra",
    ]

    def return_air_damper(self, data):
        if data["q_heat"] > 0:
            if (
                abs(data["pos_damper_ra"] - data["pos_damper_ra_max"])
                < data["tol_pos_damper_ra"]
            ):
                return True
            else:
                return False
        elif data["q_cool"] > 0:
            if data["pos_damper_ra"] < data["tol_pos_damper_ra"]:
                return True
            else:
                return False
        elif 0 < data["pos_damper_ra"] < data["pos_damper_ra_max"]:
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
