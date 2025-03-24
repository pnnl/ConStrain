"""
### Description

This verification aims to check if the relief air damper operates correctly in systems with return fan airflow tracking. The damper position should respond appropriately to heating/cooling modes and coordinate with return air damper position to maintain proper building pressure.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Relief Air Damper Control with Return Fan Airflow Tracking

### Verification Approach

The verification checks relief air damper position under three conditions:
1. During heating: damper should be fully closed
2. During cooling: damper should be at maximum position
3. Otherwise: damper position should complement return air damper position

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with return fans using airflow tracking
- Climate Zone(s): any
- Component(s): relief air dampers, return fans, airflow sensors

### Verification Algorithm Pseudo Code

```python
if out_htg > 0:
    if abs(pos_damper_rea - 0) < tol_pos_damper_rea:
        pass
    else:
        fail
elif out_clg > 0:
    if abs(pos_damper_rea - pos_damper_rea_max) < tol_pos_damper_rea:
        pass
    else:
        fail
elif abs(pos_damper_rea - (1 - pos_damper_ra) * pos_damper_rea_max) < tol_pos_damper_rea:
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

- pos_damper_rea: Relief air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Relief air damper position
  - Data Point Affiliation: Air handling unit

- pos_damper_rea_max: Maximum relief air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Maximum relief air damper position
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_rea: Relief air damper position tolerance
  - Data Value Unit: percent
  - Data point Description: Relief air damper position tolerance
  - Data Point Affiliation: Air handling unit

- pos_damper_ra: Return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Return air damper position
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReliefAirDamperPositionForReturnFanAirflowTracking(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "rea_p",
        "max_rea_p",
        "rea_p_tol",
        "ra_p",
    ]

    def relief_air_damper(self, data):
        if data["heating_output"] > 0:
            if data["rea_p"] < data["rea_p_tol"]:
                return True
            else:
                return False
        elif data["cooling_output"] > 0:
            if abs(data["rea_p"] - data["max_rea_p"]) < data["rea_p_tol"]:
                return True
            else:
                return False
        elif (
            abs(data["rea_p"] - (1 - data["ra_p"]) * data["max_rea_p"])
            < data["rea_p_tol"]
        ):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.relief_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
