"""
### Description

This verification aims to check if the return air damper operates correctly in systems with return fan airflow tracking. The damper position should respond appropriately to heating/cooling modes and coordinate with relief air damper position to maintain proper building pressure.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Return Air Damper Control with Return Fan Airflow Tracking

### Verification Approach

The verification checks return air damper position under three conditions:
1. During heating: damper should be at maximum position
2. During cooling: damper should be fully closed
3. Otherwise: damper position should complement relief air damper position

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with return fans using airflow tracking
- Climate Zone(s): any
- Component(s): return air dampers, return fans, relief air dampers

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
elif abs(ra_p - (1 - rea_p) * max_ra_p) < ra_p_tol:
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

- rea_p: Relief air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current relief air damper position
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReturnFanAirflowTracking(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "ra_p",
        "max_ra_p",
        "ra_p_tol",
        "rea_p",
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
        elif (
            abs(data["ra_p"] - (1 - data["rea_p"]) * data["max_ra_p"])
            < data["ra_p_tol"]
        ):
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
