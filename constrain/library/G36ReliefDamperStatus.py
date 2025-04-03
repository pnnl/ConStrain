"""
### Description

Section 5.16.8.1. 
- Relief dampers shall be enabled when the associated supply fan is proven ON, and disabled otherwise.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.8 Relief Damper Control
- Code Subsection: 5.16.8.1 Relief Damper Enable/Disable

### Verification Approach

The verification checks two conditions:
1. When supply fan is ON, relief damper is allowed to modulate open
2. When supply fan is OFF, relief damper must be fully closed
The test is considered untested if supply fan status doesn't show both ON and OFF states.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with relief dampers
- Climate Zone(s): any
- Component(s): relief dampers, supply fans

### Verification Algorithm Pseudo Code

```python
if position_damper_relief > 0 and status_fan_supply == 'on':
    pass
elif status_fan_supply == 'off' and position_damper_relief == 0:
    pass
else:
    fail

if not ['on', 'off'] in status_fan_supply:
    untested
```

### Data requirements

- position_damper_relief: Relief damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- status_fan_supply: Supply fan status
  - Data Value Unit: binary
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReliefDamperStatus(RuleCheckBase):
    points = ["position_damper_relief", "status_fan_supply"]

    def ts_verify_logic(self, t):
        if t["position_damper_relief"] > self.get_tolerance(
            "damper", "command"
        ) and bool(t["status_fan_supply"]):
            return True
        elif t["position_damper_relief"] < (
            (1 - self.get_tolerance("damper", "command")) * 100
        ) and not bool(t["status_fan_supply"]):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            obs_satuses = [bool(s) for s in list(self.df["status_fan_supply"].unique())]
            if (True in obs_satuses) and (False in obs_satuses):
                return True
            else:
                return "Untested"
