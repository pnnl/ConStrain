"""
### Description

This verification aims to check if the outdoor air damper control operates correctly based on occupancy. The system should close outdoor air dampers when spaces are not occupied, except during economizer operation.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3 Controls and Diagnostics
- Code Subsection: 6.4.3.4.2 Automatic Outdoor Air Damper Control

### Verification Approach

The verification checks that when a space is unoccupied and the economizer is not active, the outdoor air and exhaust air dampers should be closed (flow rates near zero). The verification passes if this condition is met.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): HVAC systems with outdoor air dampers
- Climate Zone(s): any
- Component(s): outdoor air dampers, exhaust air dampers

### Verification Algorithm Pseudo Code

```
if n_occ <= 0 + tol and v_ea + v_oa > 0 and flag_econ = 0
    return false
else
    return pass
```

### Data requirements

- n_occ: Number of occupants
  - Data Value Unit: count
  - Data point Description: Number of occupants
  - Data Point Affiliation: Zone occupancy

- v_oa: System outdoor air volume flow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Outdoor air volume flow rate
  - Data Point Affiliation: System ventilation

- v_ea: System exhaust air volume flow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Exhaust air volume flow rate
  - Data Point Affiliation: System ventilation

- flag_econ: System air-side economizer status
  - Data Value Unit: binary (0/1)
  - Data point Description: Economizer flag
  - Data Point Affiliation: System operation

- tol_n_occ: Tolerance for occupancy
  - Data Value Unit: count
  - Data point Description: Occupancy tolerance
  - Data Point Affiliation: Zone occupancy

- tol_v_oa: Tolerance for outdoor air flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Outdoor air volume flow rate tolerance
  - Data Point Affiliation: System ventilation

- tol_v_ea: Tolerance for exhaust air flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Exhaust air volume flow rate tolerance
  - Data Point Affiliation: System ventilation

"""

from constrain.checklib import RuleCheckBase


class AutomaticOADamperControl(RuleCheckBase):
    points = ["o", "eco_onoff", "m_oa", "m_ea", "tol_o", "tol_m_oa", "tol_m_ea"]

    def automatic_oa_damper_check(self, data):
        if data["o"] < data["tol_o"]:
            if data["eco_onoff"] == 0 and (
                float(data["m_oa"]) >= data["tol_m_oa"]
                or float(data["m_ea"]) >= data["tol_m_ea"]
            ):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.automatic_oa_damper_check(d), axis=1)
