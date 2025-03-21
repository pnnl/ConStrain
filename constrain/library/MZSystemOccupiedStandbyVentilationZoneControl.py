"""
### Description

This verification aims to check if multiple-zone systems properly adjust their outdoor air setpoints when zones enter standby mode. The system should reduce outdoor air flow by at least the amount that would have been required for zones now in standby.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2022
- Code Section: 6.5.3.9 Multiple-Zone System Ventilation Optimization Control
- Code Subsection: 6.5.3.9.1 Occupied-Standby Control

### Verification Approach

The verification monitors outdoor air setpoint adjustments:
1. Track system outdoor air setpoint before and during standby
2. Calculate minimum required reduction based on zone requirements
3. When zone enters standby:
   - Compare actual reduction to required reduction
   - Pass if reduction meets or exceeds requirement
4. Mark as untested when zone is not in standby

### Verification Applicability

- Building Type(s): any with multiple zones
- Space Type(s): any with variable occupancy
- System(s): multiple-zone air handling units
- Climate Zone(s): any
- Component(s): outdoor air dampers, occupancy sensors

### Verification Algorithm Pseudo Code

```python
if zone_is_standby_mode:
    oa_reduction = last_active_oa_setpoint - current_oa_setpoint
    if oa_reduction >= zone_oa_requirement:
        pass  # Proper setpoint reduction
    else:
        fail  # Insufficient reduction
else:
    last_active_oa_setpoint = current_oa_setpoint
    untested  # Cannot verify without standby condition
```

### Data requirements

- zone_is_standby_mode: Standby status
  - Data Value Unit: boolean
  - Data point Description: Indicates if zone is in standby mode
  - Data Point Affiliation: Zone control

- m_oa_requested_by_system: System OA setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current system outdoor air flow setpoint
  - Data Point Affiliation: System control

- m_oa_zone_requirement: Zone OA requirement
  - Data Value Unit: volumetric flow rate
  - Data point Description: Required outdoor air flow for zone
  - Data Point Affiliation: Zone ventilation

"""

from constrain.checklib import RuleCheckBase


class MZSystemOccupiedStandbyVentilationZoneControl(RuleCheckBase):
    points = [
        "zone_is_standby_mode",
        "m_oa_requested_by_system",
        "m_oa_zone_requirement",
    ]
    last_non_standby_mode_requested_m_oa = None  # expects kg/s

    def occupied_standby_ventilation_zontrol_control(self, data):
        # initialization
        if self.last_non_standby_mode_requested_m_oa is None:
            self.last_non_standby_mode_requested_m_oa = data["m_oa_requested_by_system"]
        # verification
        if data["zone_is_standby_mode"]:
            if (
                self.last_non_standby_mode_requested_m_oa
                - data["m_oa_requested_by_system"]
            ) >= data["m_oa_zone_requirement"]:
                return True
            else:
                return False
        else:
            self.last_non_standby_mode_requested_m_oa = data["m_oa_requested_by_system"]
            return "Untested"

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.occupied_standby_ventilation_zontrol_control(d), axis=1
        )
