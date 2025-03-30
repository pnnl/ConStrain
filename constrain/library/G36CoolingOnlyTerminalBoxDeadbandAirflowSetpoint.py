"""
### Description

Section 5.5.5.2
- When the Zone State is deadband, the active airflow setpoint shall be the minimum endpoint.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.5.5 Terminal Box Airflow Control
- Code Subsection: 5.5.5.2 Deadband Airflow Control

### Verification Approach

The verification checks that when the zone is in deadband mode, the active airflow setpoint equals the minimum value within a specified tolerance. The minimum value varies depending on whether the system is in occupied mode or other modes (cooldown/setup/warmup/setback/unoccupied).

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
    minimum = flow_volumetric_air_setpoint_min
case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied'
    minimum = 0

if abs(flow_volumetric_air_setpoint - minimum) = 0
    pass
else
    fail
end
```

### Data requirements

- mode_system: System operation mode (occupied, cooldown, setup, warmup, setback, unoccupied)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- state_zone: Zone state (if state_zone is not "deadband", this verification item falls into the "untested" result)
  - Data Value Unit: enumeration
  - Data Point Affiliation: Zone control

- flow_volumetric_air_setpoint_min: Minimum airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_setpoint: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

"""

from constrain.checklib import RuleCheckBase


class G36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
    ]

    def setpoint_at_minimum(self, mode_system, state_zone, v_min, v_sp, tol_v):
        if state_zone.lower().strip() != "deadband":
            return "Untested"
        match mode_system.strip().lower():
            case "occupied":
                dbmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                dbmin = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if abs(v_sp - dbmin) <= tol_v:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_at_minimum(
                t["mode_system"],
                t["state_zone"],
                t["flow_volumetric_air_setpoint_min"],
                t["flow_volumetric_air_setpoint"],
                self.get_tolerance("airflow", "general"),
            ),
            axis=1,
        )
