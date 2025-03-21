"""
### Description

This verification aims to check if the outdoor air damper operates correctly in systems with return fan airflow tracking. The damper should maintain a position that allows proper coordination with the return fan's airflow control strategy.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Outdoor Air Damper Control with Return Fan Airflow Tracking

### Verification Approach

The verification checks that the outdoor air damper maintains its maximum position within an acceptable tolerance. This position ensures proper building pressurization when using return fan airflow tracking control.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with return fans using airflow tracking
- Climate Zone(s): any
- Component(s): outdoor air dampers, return fans, airflow sensors

### Verification Algorithm Pseudo Code

```python
if abs(oa_p - max_oa_p) < oa_p_tol:
    pass
else:
    fail
```

### Data requirements

- oa_p: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current outdoor air damper position
  - Data Point Affiliation: Air handling unit

- max_oa_p: Maximum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum allowed outdoor air damper position
  - Data Point Affiliation: Air handling unit

- oa_p_tol: Outdoor air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReturnFanAirflowTracking(RuleCheckBase):
    points = [
        "oa_p",
        "max_oa_p",
        "oa_p_tol",
    ]

    def outdoor_air_damper(self, data):
        if abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.outdoor_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
