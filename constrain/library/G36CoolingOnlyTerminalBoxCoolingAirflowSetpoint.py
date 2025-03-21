"""
### Description

This verification aims to check if the cooling-only terminal box airflow control operates correctly when the zone is in cooling mode. The active airflow setpoint should be properly mapped between minimum and maximum cooling endpoints based on the system's operation mode.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.5.5 Terminal Box Airflow Control
- Code Subsection: 5.5.5.1 Cooling Airflow Control

### Verification Approach

The verification checks that when the zone is in cooling mode, the active airflow setpoint stays within appropriate boundaries based on the current operation mode. The boundaries vary depending on whether the system is in occupied, cooldown/setup, or warmup/setback/unoccupied mode.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV cooling-only terminal boxes
- Climate Zone(s): any
- Component(s): terminal box controllers, airflow sensors

### Verification Algorithm Pseudo Code

```
switch operation_mode
case 'occupied'
    cooling_maximum = v_cool_max
    minimum = v_min
case 'cooldown', 'setup'
    cooling_maximum = v_cool_max
    minimum = 0
case 'warmup', 'setback', 'unoccupied'
    cooling_maximum = 0
    minimum = 0

if minimum <= v_spt <= cooling_maximum
    pass
else
    fail
end
```

### Data requirements

- operation_mode: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: Current operation mode of the system
  - Data Point Affiliation: System control

- zone_state: Zone state
  - Data Value Unit: enumeration
  - Data point Description: Current zone state (heating, cooling, or deadband)
  - Data Point Affiliation: Zone control

- v_cool_max: Maximum cooling airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Maximum cooling airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_min: Minimum airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Occupied zone minimum airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_spt: Active airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current active airflow setpoint
  - Data Point Affiliation: Zone airflow control

"""

from constrain.checklib import RuleCheckBase


class G36CoolingOnlyTerminalBoxCoolingAirflowSetpoint(RuleCheckBase):
    points = ["operation_mode", "zone_state", "v_cool_max", "v_min", "v_spt"]

    def setpoint_in_range(self, operation_mode, zone_state, v_cool_max, v_min, v_spt):
        if zone_state.lower().strip() != "cooling":
            return "Untested"
        match operation_mode.strip().lower():
            case "occupied":
                cooling_maximum = v_cool_max
                cooling_minimum = v_min
            case "cooldown" | "setup":
                cooling_maximum = v_cool_max
                cooling_minimum = 0
            case "warmup" | "setback" | "unoccupied":
                cooling_maximum = 0
                cooling_minimum = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if cooling_minimum <= v_spt <= cooling_maximum:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["operation_mode"],
                t["zone_state"],
                t["v_cool_max"],
                t["v_min"],
                t["v_spt"],
            ),
            axis=1,
        )
