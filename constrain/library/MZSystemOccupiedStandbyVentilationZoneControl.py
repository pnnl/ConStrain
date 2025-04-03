"""
### Description

Section 6.5.3.9.1 Occupied-Standby Control of Multiple-Zone Systems
- Multi-zone systems with ventilation optimization shall reset their outdoor air setpoint assuming that all zones in standby mode don't require any outdoor air.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2022
- Code Section: 6.5.3.9.1 Occupied-Standby Control of Multiple-Zone Systems

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
if flag_zone_standby:
    oa_reduction = last_active_oa_setpoint - flow_volumetric_air_outdoor_system_setpoint
    if oa_reduction >= flow_volumetric_air_outdoor_zone_req:
        pass  # Proper setpoint reduction
    else:
        fail  # Insufficient reduction
else:
    last_active_oa_setpoint = flow_volumetric_air_outdoor_system_setpoint
    untested  # Cannot verify without standby condition
```

### Data requirements

- flag_zone_standby: Standby flag
  - Data Value Unit: binary
  - Data Point Affiliation: Zone control

- flow_volumetric_air_outdoor_system_setpoint: System OA setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: System control

- flow_volumetric_air_outdoor_zone_req: Zone OA requirement
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone ventilation

"""

from constrain.checklib import RuleCheckBase


class MZSystemOccupiedStandbyVentilationZoneControl(RuleCheckBase):
    points = [
        "flag_zone_standby",
        "flow_volumetric_air_outdoor_system_setpoint",
        "flow_volumetric_air_outdoor_zone_req",
    ]
    last_non_standby_mode_requested_v_oa = None  # expects volumetric flow rate

    def occupied_standby_ventilation_zone_control(self, data):
        # initialization
        if self.last_non_standby_mode_requested_v_oa is None:
            self.last_non_standby_mode_requested_v_oa = data[
                "flow_volumetric_air_outdoor_system_setpoint"
            ]
        # verification
        if data["flag_zone_standby"]:
            if (
                self.last_non_standby_mode_requested_v_oa
                - data["flow_volumetric_air_outdoor_system_setpoint"]
            ) >= (
                data["flow_volumetric_air_outdoor_zone_req"]
                - self.get_tolerance("airflow", "outdoor_air")
            ):
                return True
            else:
                return False
        else:
            self.last_non_standby_mode_requested_v_oa = data[
                "flow_volumetric_air_outdoor_system_setpoint"
            ]
            return "Untested"

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.occupied_standby_ventilation_zone_control(d), axis=1
        )
