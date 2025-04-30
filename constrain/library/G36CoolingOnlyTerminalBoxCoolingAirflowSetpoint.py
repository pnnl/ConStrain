"""
### Description

Section 5.5.5.1   
- When the Zone State is cooling, the cooling-loop output shall be mapped to the active airflow setpoint from the minimum endpoint to the cooling maximum endpoint.

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
switch mode_system
case 'occupied'
    cooling_maximum = flow_volumetric_air_cool_max
    minimum = flow_volumetric_air_setpoint_min
case 'cooldown', 'setup'
    cooling_maximum = flow_volumetric_air_cool_max
    minimum = 0
case 'warmup', 'setback', 'unoccupied'
    cooling_maximum = 0
    minimum = 0

if minimum <= flow_volumetric_air_setpoint <= cooling_maximum
    pass
else
    fail
end
```

### Data requirements

- mode_system: System operation mode (occupied, cooldown, setup, warmup, setback, unoccupied)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- state_zone: Zone state (if state_zone is not "cooling", this verification item falls into the "untested" result)
  - Data Value Unit: enumeration
  - Data Point Affiliation: Zone control

- flow_volumetric_air_cool_max: Maximum cooling airflow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_setpoint_min: minimum airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_setpoint: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

"""

from constrain.checklib import RuleCheckBase


class G36CoolingOnlyTerminalBoxCoolingAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_cool_max",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
    ]

    def setpoint_in_range(self, mode_system, state_zone, v_cool_max, v_min, v_sp):
        if state_zone.lower().strip() != "cooling":
            return "Untested"
        match mode_system.strip().lower():
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

        if cooling_minimum <= v_sp <= cooling_maximum:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["mode_system"],
                t["state_zone"],
                t["flow_volumetric_air_cool_max"],
                t["flow_volumetric_air_setpoint_min"],
                t["flow_volumetric_air_setpoint"],
            ),
            axis=1,
        )
