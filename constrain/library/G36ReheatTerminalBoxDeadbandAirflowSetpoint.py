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
if t_vav_dis > t_vav_dis_min and cmd_htg_coil > tol_cmd_htg_coil:
    fail
else:
    switch mode_sys:
        case 'occupied':
            minimum = v_vav_min
        case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied':
            minimum = 0

    if abs(v_vav_sp - minimum) <= tol_v_vav:
        pass
    else:
        fail
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

- cmd_htg_coil: Heating coil command
  - Data Value Unit: percent (0-100)
  - Data point Description: Heating coil command
  - Data Point Affiliation: Terminal box control

- tol_cmd_htg_coil: Heating coil command tolerance
  - Data Value Unit: percent
  - Data point Description: Heating coil command tolerance
  - Data Point Affiliation: Terminal box control

- t_vav_dis: VAV discharge air temperature
  - Data Value Unit: °C
  - Data point Description: VAV discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

- t_vav_dis_min: Minimum VAV discharge air temperature
  - Data Value Unit: °C
  - Data point Description: Minimum VAV discharge air temperature
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
