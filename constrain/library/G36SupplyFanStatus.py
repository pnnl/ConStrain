"""
### Description

Section 5.16.1.1
- a. Supply fan shall run when system is in the Cooldown Mode, Setup Mode, or Occupied Mode.
- b. If there are any VAV-reheat boxes on perimeter zones, supply fan shall also run when system is in Setback Mode or Warmup Mode (i.e., all modes except unoccupied).

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.1 Supply Fan Control
- Code Subsection: 5.16.1.1 Supply Fan Operation

### Verification Approach

The verification checks two scenarios:
1. For systems with perimeter VAV reheat boxes:
   - Fan must run in all modes except unoccupied
2. For systems without perimeter VAV reheat boxes:
   - Fan must run in cooldown, setup, and occupied modes only
The test is considered untested if both occupied and unoccupied modes haven't been observed.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units
- Climate Zone(s): any
- Component(s): supply fans, VAV boxes, zone configuration

### Verification Algorithm Pseudo Code

```python
if flag_reheat_perimeter:
    if mode_system != 'unoccupied' and status_fan_supply == 'off':
        fail
    else:
        pass
else:
    if mode_system in ['occupied', 'setup', 'cooldown'] and status_fan_supply == 'off':
        fail
    else:
        pass

if not ('occupied' in mode_system and 'unoccupied' in mode_system):
    untested
```

### Data requirements

- mode_system: System mode ("occupied", "unoccupied", "setup", "cooldown")
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- flag_reheat_perimeter: Zone configuration flag
  - Data Value Unit: binary
  - Data Point Affiliation: System configuration

- status_fan_supply: Supply fan status
  - Data Value Unit: binary
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36SupplyFanStatus(RuleCheckBase):
    points = ["mode_system", "status_fan_supply", "flag_reheat_perimeter"]

    def ts_verify_logic(self, t):
        if bool(t["flag_reheat_perimeter"]):
            if (t["mode_system"].strip().lower() != "unoccupied") and (
                not bool(t["status_fan_supply"])
            ):
                return False
            return True
        else:
            if (
                t["mode_system"].strip().lower() in ["occupied", "setup", "cooldown"]
            ) and (not bool(t["status_fan_supply"])):
                return False
            return True

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            obs_modes = [
                s.lower().strip() for s in list(self.df["mode_system"].unique())
            ]
            if ("occupied" in obs_modes) and ("unoccupied" in obs_modes):
                return True
            else:
                return "Untested"
