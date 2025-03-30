"""
### Description

Section 5.16.2.3
- Supply air temperature shall be controlled to setpoint using a control loop whose output is mapped to sequence the heating coil (if applicable), outdoor air damper, return air damper, and cooling coil

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
if output_coil_heating > 0:
    if abs(position_damper_air_return - position_damper_air_return_max) = 0:
        pass
    else:
        fail
elif output_coil_cooling > 0:
    if abs(position_damper_air_return - 0) = 0:
        pass
    else:
        fail
elif abs(position_damper_air_return - (1 - position_damper_relief) * position_damper_air_return_max) = 0:
    pass
else:
    fail
```

### Data requirements

- output_coil_heating: Heating signal
  - Data Value Unit: percent
  - Data Point Affiliation: System control

- output_coil_cooling: Cooling signal
  - Data Value Unit: percent
  - Data Point Affiliation: System control

- position_damper_air_return: Return air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_return_max: Maximum return air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_relief: Relief air damper position
  - Data Value Unit: percent
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
