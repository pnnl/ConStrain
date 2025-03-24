"""
### Description

This verification aims to check if the supply fan operates correctly based on system mode and zone configuration. The fan operation requirements vary depending on whether the system serves VAV reheat boxes in perimeter zones.

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
if flag_vav_reheat_perimeter:
    if mode_sys != 'unoccupied' and flag_fan_sa == 'off':
        fail
    else:
        pass
else:
    if mode_sys in ['occupied', 'setup', 'cooldown'] and flag_fan_sa == 'off':
        fail
    else:
        pass

if not ('occupied' in mode_sys and 'unoccupied' in mode_sys):
    untested
```

### Data requirements

- mode_sys: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System operation mode
  - Data Point Affiliation: System control

- flag_vav_reheat_perimeter: Zone configuration
  - Data Value Unit: binary
  - Data point Description: VAV reheat perimeter flag
  - Data Point Affiliation: System configuration

- flag_fan_sa: Supply fan status
  - Data Value Unit: binary
  - Data point Description: Supply fan status
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36SupplyFanStatus(RuleCheckBase):
    points = ["sys_mode", "supply_fan_status", "has_reheat_box_on_perimeter_zones"]

    def ts_verify_logic(self, t):
        if bool(t["has_reheat_box_on_perimeter_zones"]):
            if (t["sys_mode"].strip().lower() != "unoccupied") and (
                not bool(t["supply_fan_status"])
            ):
                return False
            return True
        else:
            if (
                t["sys_mode"].strip().lower() in ["occupied", "setup", "cooldown"]
            ) and (not bool(t["supply_fan_status"])):
                return False
            return True

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            obs_modes = [s.lower().strip() for s in list(self.df["sys_mode"].unique())]
            if ("occupied" in obs_modes) and ("unoccupied" in obs_modes):
                return True
            else:
                return "Untested"
