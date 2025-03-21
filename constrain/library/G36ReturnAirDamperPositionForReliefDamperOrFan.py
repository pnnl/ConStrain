"""
### Description

This verification aims to check if the return air damper operates correctly in systems with relief dampers or fans. The damper position should respond appropriately to heating/cooling modes and coordinate with outdoor air damper position to maintain proper building pressure.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Return Air Damper Control with Relief Damper/Fan

### Verification Approach

The verification checks return air damper position under four conditions:
1. During heating: damper should be at maximum position
2. During cooling: damper should be fully closed
3. When outdoor air damper is below maximum: return damper should be at maximum
4. When outdoor air damper is at maximum: return damper should be below maximum

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with relief dampers or fans
- Climate Zone(s): any
- Component(s): return air dampers, relief dampers/fans, outdoor air dampers

### Verification Algorithm Pseudo Code

```python
if heating_output > 0:
    if abs(ra_p - max_ra_p) < ra_p_tol:
        pass
    else:
        fail
elif cooling_output > 0:
    if abs(ra_p - 0) < ra_p_tol:
        pass
    else:
        fail
elif oa_p < max_oa_p:
    if abs(ra_p - max_ra_p) < ra_p_tol:
        pass
    else:
        fail
elif abs(oa_p - max_oa_p) < oa_p_tol:
    if ra_p < max_ra_p:
        pass
    else:
        fail
```

### Data requirements

- heating_output: Heating output
  - Data Value Unit: percent (0-100)
  - Data point Description: Current heating system output
  - Data Point Affiliation: System control

- cooling_output: Cooling output
  - Data Value Unit: percent (0-100)
  - Data point Description: Current cooling system output
  - Data Point Affiliation: System control

- ra_p: Return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current return air damper position
  - Data Point Affiliation: Air handling unit

- max_ra_p: Maximum return air position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum allowed return air damper position
  - Data Point Affiliation: Air handling unit

- ra_p_tol: Return air position tolerance
  - Data Value Unit: percent
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Air handling unit

- oa_p: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current outdoor air damper position
  - Data Point Affiliation: Air handling unit

- max_oa_p: Maximum outdoor air position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum allowed outdoor air damper position
  - Data Point Affiliation: Air handling unit

- oa_p_tol: Outdoor air position tolerance
  - Data Value Unit: percent
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "ra_p",
        "max_ra_p",
        "ra_p_tol",
        "oa_p",
        "max_oa_p",
        "oa_p_tol",
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
        elif data["oa_p"] < data["max_oa_p"]:
            if abs(data["ra_p"] - data["max_ra_p"]) < data["ra_p_tol"]:
                return True
            else:
                return False
        elif abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
            if data["ra_p"] < data["max_ra_p"]:
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.return_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if len(self.result[self.result == "Untested"] > 0):
                return "Untested"
            else:
                return True
