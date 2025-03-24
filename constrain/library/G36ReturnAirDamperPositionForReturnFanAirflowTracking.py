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
if out_htg > 0:
    if abs(pos_damper_ra - pos_damper_ra_max) < tol_pos_damper_ra:
        pass
    else:
        fail
elif out_clg > 0:
    if abs(pos_damper_ra - 0) < tol_pos_damper_ra:
        pass
    else:
        fail
elif abs(pos_damper_ra - (1 - pos_damper_rea) * pos_damper_ra_max) < tol_pos_damper_ra:
    pass
else:
    fail
```

### Data requirements

- out_htg: Heating output
  - Data Value Unit: percent (0-100)
  - Data point Description: Heating output
  - Data Point Affiliation: System control

- out_clg: Cooling output
  - Data Value Unit: percent (0-100)
  - Data point Description: Cooling output
  - Data Point Affiliation: System control

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

- pos_damper_rea: Relief air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Relief air damper position
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
