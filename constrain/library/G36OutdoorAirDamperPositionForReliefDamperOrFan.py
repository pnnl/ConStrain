"""
### Description

Section 5.16.2.3
- Supply air temperature shall be controlled to setpoint using a control loop whose output is mapped to sequence the heating coil (if applicable), outdoor air damper, return air damper, and cooling coil.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
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
if output_coil_heating > 0:
    if abs(position_damper_air_outdoor - position_damper_air_outdoor_min) = 0:
        pass
    else:
        fail
elif output_coil_cooling > 0:
    if flag_economizer_limit:
        if abs(position_damper_air_outdoor - position_damper_air_outdoor_min) = 0:
            pass
        else:
            fail
    else:
        if abs(position_damper_air_outdoor - position_damper_air_outdoor_max) = 0:
            pass
        else:
            fail
elif position_damper_air_return < position_damper_air_return_max:
    if abs(position_damper_air_outdoor - position_damper_air_outdoor_max) = 0:
        pass
    else:
        fail
elif abs(position_damper_air_return - position_damper_air_return_max) = 0:
    if position_damper_air_outdoor_min < position_damper_air_outdoor < position_damper_air_outdoor_max:
        pass
    else:
        fail
else:
    untested
```

### Data requirements

- output_coil_heating: Heating signal
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- output_coil_cooling: Cooling signal
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_return: Return air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_return_max: Maximum return air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor_min: Minimum outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor_max: Maximum outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- flag_economizer_limit: Economizer high limit flag
  - Data Value Unit: binary
  - Data Point Affiliation: Economizer control

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "output_coil_heating",
        "output_coil_cooling",
        "position_damper_air_return",
        "position_damper_air_return_max",
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_min",
        "position_damper_air_outdoor_max",
        "flag_economizer_limit",
    ]

    def outdoor_air_damper(self, data):
        if data["output_coil_heating"] > 0:
            if abs(
                data["position_damper_air_outdoor"]
                - data["position_damper_air_outdoor_min"]
            ) < self.get_tolerance("damper", "position"):
                return True
            else:
                return False
        elif data["output_coil_cooling"] > 0:
            if data["flag_economizer_limit"]:
                if abs(
                    data["position_damper_air_outdoor"]
                    - data["position_damper_air_outdoor_min"]
                ) < self.get_tolerance("damper", "position"):
                    return True
                else:
                    return False
            else:
                if abs(
                    data["position_damper_air_outdoor"]
                    - data["position_damper_air_outdoor_max"]
                ) < self.get_tolerance("damper", "position"):
                    return True
                else:
                    return False
        elif (
            data["position_damper_air_return"] < data["position_damper_air_return_max"]
        ):
            if abs(
                data["position_damper_air_outdoor"]
                - data["position_damper_air_outdoor_max"]
            ) < self.get_tolerance("damper", "position"):
                return True
            else:
                return False
        elif abs(
            data["position_damper_air_return"] - data["position_damper_air_return_max"]
        ) < self.get_tolerance("damper", "position"):
            if (
                data["position_damper_air_outdoor_min"]
                < data["position_damper_air_outdoor"]
                < data["position_damper_air_outdoor_max"]
            ):
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
