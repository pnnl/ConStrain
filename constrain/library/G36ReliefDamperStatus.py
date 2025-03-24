"""
### Description

This verification aims to check if relief dampers are properly interlocked with their associated supply fans. Relief dampers should only be enabled when their corresponding supply fan is proven to be running.

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
if pos_damper_rea > 0 and flag_fan_sa == 'on':
    pass
elif flag_fan_sa == 'off' and pos_damper_rea == 0:
    pass
else:
    fail

if not ['on', 'off'] in flag_fan_sa:
    untested
```

### Data requirements

- pos_damper_rea: Relief damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Relief damper position
  - Data Point Affiliation: Air handling unit

- flag_fan_sa: Supply fan status
  - Data Value Unit: binary
  - Data point Description: Supply fan status
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReliefDamperStatus(RuleCheckBase):
    points = ["relief_damper_command", "supply_fan_status"]

    def ts_verify_logic(self, t):
        if t["relief_damper_command"] > 0 and bool(t["supply_fan_status"]):
            return True
        elif t["relief_damper_command"] < 1 and (not bool(t["supply_fan_status"])):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            obs_satuses = [bool(s) for s in list(self.df["supply_fan_status"].unique())]
            if (True in obs_satuses) and (False in obs_satuses):
                return True
            else:
                return "Untested"
