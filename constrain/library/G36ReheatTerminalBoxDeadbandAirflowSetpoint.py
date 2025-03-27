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
if t_discharge > t_discharge_min_sp and cmd_coil_heat > tol_cmd_coil_heat:
    fail
else:
    switch mode_system:
        case 'occupied':
            minimum = v_min
        case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied':
            minimum = 0

    if abs(v_sp - minimum) <= tol_v:
        pass
    else:
        fail
```

### Data requirements

- mode_system: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System mode
  - Data Point Affiliation: System control

- state_zone: Zone state
  - Data Value Unit: enumeration
  - Data point Description: Zone state (heating, cooling, or deadband)
  - Data Point Affiliation: Zone control

- v_min: Minimum airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum airflow setpoint during occupied mode
  - Data Point Affiliation: Zone airflow control

- v_sp: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Airflow setpoint
  - Data Point Affiliation: Zone airflow control

- tol_v: Airflow tolerance
  - Data Value Unit: volumetric flow rate
  - Data point Description: Airflow tolerance
  - Data Point Affiliation: Zone airflow control

- cmd_coil_heat: Heating coil command
  - Data Value Unit: percent
  - Data point Description: Heating coil command
  - Data Point Affiliation: Terminal box control

- tol_cmd_coil_heat: Heating coil command tolerance
  - Data Value Unit: percent
  - Data point Description: Heating coil command tolerance
  - Data Point Affiliation: Terminal box control

- t_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data point Description: Discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

- t_discharge_min_sp: Minimum discharge air temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Minimum discharge air temperature setpoint
  - Data Point Affiliation: Terminal box control

"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxDeadbandAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
        "tol_v",
        "command_coil_heat",
        "tol_cmd_coil_heat",
        "temperature_air_discharge",
        "temperature_air_discharge_setpoint_min",
    ]

    def setpoint_at_minimum(
        self,
        mode_system,
        state_zone,
        v_min,
        v_sp,
        tol_v,
        cmd_coil_heat,
        tol_cmd_coil_heat,
        t_discharge,
        t_discharge_min_sp,
    ):
        if state_zone.lower().strip() != "deadband":
            return "Untested"
        if t_discharge > t_discharge_min_sp and cmd_coil_heat > tol_cmd_coil_heat:
            return False
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
                t["tol_v"],
                t["command_coil_heat"],
                t["tol_cmd_coil_heat"],
                t["temperature_air_discharge"],
                t["temperature_air_discharge_setpoint_min"],
            ),
            axis=1,
        )
