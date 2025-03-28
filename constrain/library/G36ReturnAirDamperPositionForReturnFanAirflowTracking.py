"""
### Description

This verification aims to check if the return air damper operates correctly in systems with return fan airflow tracking. The damper position should respond appropriately to heating/cooling modes and coordinate with relief air damper position to maintain proper building pressure.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
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
if q_heat > 0:
    if abs(pos_damper_ra - pos_damper_ra_max) < tol_pos_damper_ra:
        pass
    else:
        fail
elif q_cool > 0:
    if abs(pos_damper_ra - 0) < tol_pos_damper_ra:
        pass
    else:
        fail
elif abs(pos_damper_ra - (1 - pos_damper_relief) * pos_damper_ra_max) < tol_pos_damper_ra:
    pass
else:
    fail
```

### Data requirements

- q_heat: Heating signal
  - Data Value Unit: percent
  - Data point Description: Heating signal (0-100)
  - Data Point Affiliation: System control

- q_cool: Cooling signal
  - Data Value Unit: percent
  - Data point Description: Cooling signal (0-100)
  - Data Point Affiliation: System control

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

- pos_damper_relief: Relief air damper command
  - Data Value Unit: percent
  - Data point Description: Relief air damper command
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReturnFanAirflowTracking(RuleCheckBase):
    points = [
        "output_coil_heating",
        "output_coil_cooling",
        "position_damper_air_return",
        "position_damper_air_return_max",
        "position_damper_relief",
    ]

    def return_air_damper(self, data):
        if data["output_coil_heating"] > 0:
            if abs(
                data["position_damper_air_return"]
                - data["position_damper_air_return_max"]
            ) < self.get_tolerance("damper", "position"):
                return True
            else:
                return False
        elif data["output_coil_cooling"] > 0:
            if data["position_damper_air_return"] < self.get_tolerance(
                "damper", "position"
            ):
                return True
            else:
                return False
        elif abs(
            data["position_damper_air_return"]
            - (1 - data["position_damper_relief"])
            * data["position_damper_air_return_max"]
        ) < self.get_tolerance("damper", "position"):
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
