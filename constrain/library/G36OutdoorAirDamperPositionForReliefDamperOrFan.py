"""
### Description

This verification aims to check if the outdoor air damper operates correctly in systems with relief dampers or fans. The damper position should respond appropriately to heating/cooling modes and economizer status while coordinating with return air damper position.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
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
if out_htg > 0:
    if abs(pos_damper_oa - pos_damper_oa_min) < tol_pos_damper_oa:
        pass
    else:
        fail
elif out_clg > 0:
    if flag_econ_hl:
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

- out_htg: Heating output
  - Data Value Unit: percent (0-100)
  - Data point Description: Heating output
  - Data Point Affiliation: Air handling unit

- out_clg: Cooling output
  - Data Value Unit: percent (0-100)
  - Data point Description: Cooling output
  - Data Point Affiliation: Air handling unit

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

- pos_damper_oa: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Outdoor air damper position
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_min: Minimum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Minimum outdoor air damper position
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_max: Maximum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum outdoor air damper position
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_oa: Outdoor air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper position tolerance
  - Data Point Affiliation: Air handling unit

- flag_econ_hl: Economizer high limit flag
  - Data Value Unit: binary
  - Data point Description: Economizer high limit flag
  - Data Point Affiliation: Economizer control

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "ra_p",
        "max_ra_p",
        "ra_p_tol",
        "oa_p",
        "min_oa_p",
        "max_oa_p",
        "oa_p_tol",
        "economizer_high_limit_reached",
    ]

    def outdoor_air_damper(self, data):
        if data["heating_output"] > 0:
            if abs(data["oa_p"] - data["min_oa_p"]) < data["oa_p_tol"]:
                return True
            else:
                return False
        elif data["cooling_output"] > 0:
            if data["economizer_high_limit_reached"]:
                if abs(data["oa_p"] - data["min_oa_p"]) < data["oa_p_tol"]:
                    return True
                else:
                    return False
            else:
                if abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
                    return True
                else:
                    return False
        elif data["ra_p"] < data["max_ra_p"]:
            if abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
                return True
            else:
                return False
        elif abs(data["ra_p"] - data["max_ra_p"]) < data["ra_p_tol"]:
            if data["min_oa_p"] < data["oa_p"] < data["max_oa_p"]:
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
