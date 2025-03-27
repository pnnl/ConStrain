"""
### Description

This verification aims to check if the return air damper operates correctly in systems with relief dampers or fans. The damper position should respond appropriately to heating/cooling modes and coordinate with outdoor air damper position to maintain proper building pressure.

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
elif pos_damper_oa < pos_damper_oa_max:
    if abs(pos_damper_ra - pos_damper_ra_max) < tol_pos_damper_ra:
        pass
    else:
        fail
elif abs(pos_damper_oa - pos_damper_oa_max) < tol_pos_damper_oa:
    if pos_damper_ra < pos_damper_ra_max:
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

- pos_damper_oa: Outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper command
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_max: Maximum outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Maximum outdoor air damper command
  - Data Point Affiliation: Air handling unit

- tol_pos_damper_oa: Outdoor air damper command tolerance
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper command tolerance
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "output_coil_heating",
        "output_coil_cooling",
        "position_damper_air_return",
        "position_damper_air_return_max",
        "tol_pos_damper_ra",
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_max",
        "tol_pos_damper_oa",
    ]

    def return_air_damper(self, data):
        if data["output_coil_heating"] > 0:
            if (
                abs(
                    data["position_damper_air_return"]
                    - data["position_damper_air_return_max"]
                )
                < data["tol_pos_damper_ra"]
            ):
                return True
            else:
                return False
        elif data["output_coil_cooling"] > 0:
            if data["position_damper_air_return"] < data["tol_pos_damper_ra"]:
                return True
            else:
                return False
        elif (
            data["position_damper_air_outdoor"]
            < data["position_damper_air_outdoor_max"]
        ):
            if (
                abs(
                    data["position_damper_air_return"]
                    - data["position_damper_air_return_max"]
                )
                < data["tol_pos_damper_ra"]
            ):
                return True
            else:
                return False
        elif (
            abs(
                data["position_damper_air_outdoor"]
                - data["position_damper_air_outdoor_max"]
            )
            < data["tol_pos_damper_oa"]
        ):
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
