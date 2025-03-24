"""
### Description

This verification aims to check if the cooling-only terminal box airflow control operates correctly when the zone is in heating mode. The active airflow setpoint should be properly mapped between minimum and maximum heating endpoints based on the system's operation mode.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.5.5 Terminal Box Airflow Control
- Code Subsection: 5.5.5.3 Heating Airflow Control

### Verification Approach

The verification checks that when the zone is in heating mode, the active airflow setpoint stays within appropriate boundaries based on the current operation mode. The boundaries vary depending on whether the system is in occupied, cooldown/setup/unoccupied, or warmup/setback mode.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV cooling-only terminal boxes
- Climate Zone(s): any
- Component(s): terminal box controllers, airflow sensors

### Verification Algorithm Pseudo Code

```
switch mode_sys
case 'occupied'
    heating_maximum = v_vav_heat_max
    minimum = v_vav_min
case 'cooldown', 'setup', 'unoccupied'
    heating_maximum = 0
    minimum = 0
case 'warmup', 'setback'
    heating_maximum = v_vav_cool_max
    minimum = 0

if minimum <= v_vav_sp <= heating_maximum
    pass
else
    fail
end
```

### Data requirements

- mode_sys: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System operation mode
  - Data Point Affiliation: System control

- state_zone: Zone state
  - Data Value Unit: enumeration
  - Data point Description: Zone state (heating, cooling, or deadband)
  - Data Point Affiliation: Zone control

- v_vav_cool_max: Maximum cooling airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Maximum cooling airflow
  - Data Point Affiliation: Zone airflow control

- v_vav_heat_max: Maximum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Maximum heating airflow
  - Data Point Affiliation: Zone airflow control

- v_vav_min: Minimum airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum airflow
  - Data Point Affiliation: Zone airflow control

- v_vav_sp: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Airflow setpoint
  - Data Point Affiliation: Zone airflow control

"""

from constrain.checklib import RuleCheckBase


class G36CoolingOnlyTerminalBoxHeatingAirflowSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_cool_max",
        "v_heat_max",
        "v_min",
        "v_spt",
    ]

    def setpoint_in_range(
        self, operation_mode, zone_state, v_cool_max, v_heat_max, v_min, v_spt
    ):
        if zone_state.lower().strip() != "heating":
            return "Untested"
        match operation_mode.strip().lower():
            case "occupied":
                heating_max = v_heat_max
                heating_min = v_min
            case "cooldown" | "setup" | "unoccupied":
                heating_max = 0
                heating_min = 0
            case "warmup" | "setback":
                heating_max = v_cool_max
                heating_min = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if heating_min <= v_spt <= heating_max:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["operation_mode"],
                t["zone_state"],
                t["v_cool_max"],
                t["v_heat_max"],
                t["v_min"],
                t["v_spt"],
            ),
            axis=1,
        )
