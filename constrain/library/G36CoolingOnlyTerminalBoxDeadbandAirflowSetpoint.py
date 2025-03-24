"""
### Description

This verification aims to check if the cooling-only terminal box airflow control operates correctly when the zone is in deadband mode. The active airflow setpoint should be set to the minimum endpoint based on the system's operation mode.

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
switch mode_sys
case 'occupied'
    minimum = v_vav_min
case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied'
    minimum = 0

if abs(v_vav_sp - minimum) <= tol_v_vav
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

- v_vav_min: Minimum airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum airflow
  - Data Point Affiliation: Zone airflow control

- v_vav_sp: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Airflow setpoint
  - Data Point Affiliation: Zone airflow control

- tol_v_vav: Airflow tolerance
  - Data Value Unit: volumetric flow rate
  - Data point Description: Airflow tolerance
  - Data Point Affiliation: Zone airflow control

"""

from constrain.checklib import RuleCheckBase


class G36CoolingOnlyTerminalBoxDeadbandAirflowSetpoint(RuleCheckBase):
    points = ["operation_mode", "zone_state", "v_min", "v_spt", "v_spt_tol"]

    def setpoint_at_minimum(self, operation_mode, zone_state, v_min, v_spt, v_spt_tol):
        if zone_state.lower().strip() != "deadband":
            return "Untested"
        match operation_mode.strip().lower():
            case "occupied":
                dbmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                dbmin = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if abs(v_spt - dbmin) <= v_spt_tol:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_at_minimum(
                t["operation_mode"],
                t["zone_state"],
                t["v_min"],
                t["v_spt"],
                t["v_spt_tol"],
            ),
            axis=1,
        )
