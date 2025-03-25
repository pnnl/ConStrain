"""
### Description

This verification aims to check if the outdoor air damper operates correctly in systems with relief dampers or fans. The damper position should respond appropriately to heating/cooling modes and economizer status while coordinating with return air damper position.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
- Code Subsection: 5.16.2.3 Outdoor Air Damper Control with Relief Damper/Fan

### Verification Approach

The verification checks outdoor air damper position under various operating conditions:
1. During heating: damper should be at minimum position
2. During cooling: damper position depends on economizer status
3. When return air damper is not at maximum: outdoor air damper should be at maximum
4. When return air damper is at maximum: outdoor air damper should be between min and max

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with relief dampers or fans
- Climate Zone(s): any
- Component(s): outdoor air dampers, return air dampers, economizer controls

### Verification Algorithm Pseudo Code

```python
if q_heat > 0:
    if abs(pos_damper_oa - pos_damper_oa_min) < tol_pos_damper_oa:
        pass
    else:
        fail
elif q_cool > 0:
    if flag_economizer_limit:
        if abs(pos_damper_oa - pos_damper_oa_min) < tol_pos_damper_oa:
            pass
        else:
            fail
    else:
        if abs(pos_damper_oa - pos_damper_oa_max) < tol_pos_damper_oa:
            pass
        else:
            fail
elif pos_damper_ra < pos_damper_ra_max:
    if abs(pos_damper_oa - pos_damper_oa_max) < tol_pos_damper_ra:
        pass
    else:
        fail
elif abs(pos_damper_ra - pos_damper_ra_max) < tol_pos_damper_ra:
    if pos_damper_oa_min < pos_damper_oa < pos_damper_oa_max:
        pass
    else:
        fail
else:
    untested
```

### Data requirements

- q_heat: Heating signal
  - Data Value Unit: percent
  - Data point Description: Heating signal (0-100)
  - Data Point Affiliation: Air handling unit

- q_cool: Cooling signal
  - Data Value Unit: percent
  - Data point Description: Cooling signal (0-100)
  - Data Point Affiliation: Air handling unit

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

- pos_damper_oa: Outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper command
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_min: Minimum outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Minimum outdoor air damper command
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_max: Maximum outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Maximum outdoor air damper command
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_oa: Outdoor air damper command tolerance
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper command tolerance
  - Data Point Affiliation: Air handling unit

- flag_economizer_limit: Economizer high limit flag
  - Data Value Unit: binary
  - Data point Description: Economizer high limit flag
  - Data Point Affiliation: Economizer control

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "q_heat",
        "q_cool",
        "pos_damper_ra",
        "pos_damper_ra_max",
        "tol_pos_damper_ra",
        "pos_damper_oa",
        "pos_damper_oa_min",
        "pos_damper_oa_max",
        "tol_pos_damper_oa",
        "flag_economizer_limit",
    ]

    def outdoor_air_damper(self, data):
        if data["q_heat"] > 0:
            if (
                abs(data["pos_damper_oa"] - data["pos_damper_oa_min"])
                < data["tol_pos_damper_oa"]
            ):
                return True
            else:
                return False
        elif data["q_cool"] > 0:
            if data["flag_economizer_limit"]:
                if (
                    abs(data["pos_damper_oa"] - data["pos_damper_oa_min"])
                    < data["tol_pos_damper_oa"]
                ):
                    return True
                else:
                    return False
            else:
                if (
                    abs(data["pos_damper_oa"] - data["pos_damper_oa_max"])
                    < data["tol_pos_damper_oa"]
                ):
                    return True
                else:
                    return False
        elif data["pos_damper_ra"] < data["pos_damper_ra_max"]:
            if (
                abs(data["pos_damper_oa"] - data["pos_damper_oa_max"])
                < data["tol_pos_damper_oa"]
            ):
                return True
            else:
                return False
        elif (
            abs(data["pos_damper_ra"] - data["pos_damper_ra_max"])
            < data["tol_pos_damper_ra"]
        ):
            if (
                data["pos_damper_oa_min"]
                < data["pos_damper_oa"]
                < data["pos_damper_oa_max"]
            ):
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.outdoor_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if len(self.result[self.result == "Untested"] > 0):
                return "Untested"
            else:
                return True
