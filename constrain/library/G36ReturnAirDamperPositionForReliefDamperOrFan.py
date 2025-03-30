"""
### Description

Section 5.16.2.3
- Supply air temperature shall be controlled to setpoint using a control loop whose output is mapped to sequence the heating coil (if applicable), outdoor air damper, return air damper, and cooling coil

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
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
elif position_damper_air_outdoor < position_damper_air_outdoor_max:
    if abs(position_damper_air_return - position_damper_air_return_max) = 0:
        pass
    else:
        fail
elif abs(position_damper_air_outdoor - position_damper_air_outdoor_max) = 0:
    if position_damper_air_return < position_damper_air_return_max:
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

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor_max: Maximum outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "output_coil_heating",
        "output_coil_cooling",
        "position_damper_air_return",
        "position_damper_air_return_max",
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_max",
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
        elif (
            data["position_damper_air_outdoor"]
            < data["position_damper_air_outdoor_max"]
        ):
            if abs(
                data["position_damper_air_return"]
                - data["position_damper_air_return_max"]
            ) < self.get_tolerance("damper", "position"):
                return True
            else:
                return False

        elif abs(
            data["position_damper_air_outdoor"]
            - data["position_damper_air_outdoor_max"]
        ) < self.get_tolerance("damper", "position"):
            if (
                data["position_damper_air_return"]
                < data["position_damper_air_return_max"]
            ):
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
