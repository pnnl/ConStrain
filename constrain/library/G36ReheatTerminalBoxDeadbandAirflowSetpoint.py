"""
### Description

This verification aims to check if the terminal box with reheat operates correctly when the zone is in deadband mode. The airflow setpoint should be at minimum endpoint, and the heating coil should remain disabled unless discharge air temperature falls below minimum.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.6.5 Terminal Box Airflow Control with Reheat
- Code Subsection: 5.6.5.2 Deadband Airflow Control

### Verification Approach

The verification checks two conditions:
1. When discharge air temperature is above minimum setpoint, heating coil should remain off
2. Active airflow setpoint should equal the minimum value (which varies by operation mode) within tolerance

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV terminal boxes with reheat
- Climate Zone(s): any
- Component(s): terminal box controllers, airflow sensors, heating coils

### Verification Algorithm Pseudo Code

```python
if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol:
    fail
else:
    switch operation_mode:
        case 'occupied':
            minimum = v_min
        case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied':
            minimum = 0

    if abs(v_spt - minimum) <= v_spt_tol:
        pass
    else:
        fail
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

- v_min: Minimum airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Occupied zone minimum airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_spt: Active airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current active airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_spt_tol: Airflow tolerance
  - Data Value Unit: volumetric flow rate
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Zone airflow control

- heating_coil_command: Heating coil command
  - Data Value Unit: percent (0-100)
  - Data point Description: Current heating coil control signal
  - Data Point Affiliation: Terminal box control

- heating_coil_command_tol: Command tolerance
  - Data Value Unit: percent
  - Data point Description: Tolerance for considering heating coil active
  - Data Point Affiliation: Terminal box control

- dat: Discharge air temperature
  - Data Value Unit: °C
  - Data point Description: Current discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

- dat_min_spt: Minimum discharge temperature
  - Data Value Unit: °C
  - Data point Description: Minimum allowed discharge air temperature
  - Data Point Affiliation: Terminal box control

"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxDeadbandAirflowSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_min",
        "v_spt",
        "v_spt_tol",
        "heating_coil_command",
        "heating_coil_command_tol",
        "dat",
        "dat_min_spt",
    ]

    def setpoint_at_minimum(
        self,
        operation_mode,
        zone_state,
        v_min,
        v_spt,
        v_spt_tol,
        heating_coil_command,
        heating_coil_command_tol,
        dat,
        dat_min_spt,
    ):
        if zone_state.lower().strip() != "deadband":
            return "Untested"
        if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol:
            return False
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
                t["heating_coil_command"],
                t["heating_coil_command_tol"],
                t["dat"],
                t["dat_min_spt"],
            ),
            axis=1,
        )
