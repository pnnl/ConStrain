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
if heating_output > 0:
    if abs(oa_p - min_oa_p) < oa_p_tol:
        pass
    else:
        fail
elif cooling_output > 0:
    if economizer_high_limit_reached:
        if abs(oa_p - min_oa_p) < oa_p_tol:
            pass
        else:
            fail
    else:
        if abs(oa_p - max_oa_p) < oa_p_tol:
            pass
        else:
            fail
elif ra_p < max_ra_p:
    if abs(oa_p - max_oa_p) < ra_p_tol:
        pass
    else:
        fail
elif abs(ra_p - max_ra_p) < ra_p_tol:
    if min_oa_p < oa_p < max_oa_p:
        pass
    else:
        fail
else:
    untested
```

### Data requirements

- heating_output: Heating coil output
  - Data Value Unit: percent (0-100)
  - Data point Description: Current heating coil output
  - Data Point Affiliation: Air handling unit

- cooling_output: Cooling coil output
  - Data Value Unit: percent (0-100)
  - Data point Description: Current cooling coil output
  - Data Point Affiliation: Air handling unit

- ra_p: Return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current return air damper position
  - Data Point Affiliation: Air handling unit

- max_ra_p: Maximum return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum allowed return air damper position
  - Data Point Affiliation: Air handling unit

- ra_p_tol: Return air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Air handling unit

- oa_p: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current outdoor air damper position
  - Data Point Affiliation: Air handling unit

- min_oa_p: Minimum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Minimum allowed outdoor air damper position
  - Data Point Affiliation: Air handling unit

- max_oa_p: Maximum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum allowed outdoor air damper position
  - Data Point Affiliation: Air handling unit

- oa_p_tol: Outdoor air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Air handling unit

- economizer_high_limit_reached: Economizer status
  - Data Value Unit: binary
  - Data point Description: Indicates if economizer high limit is reached
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
