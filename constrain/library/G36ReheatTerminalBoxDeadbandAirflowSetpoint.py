"""
### Description

Section 5.6.5.2
- When the Zone State is deadband, the active airflow setpoint shall be the minimum endpoint. Heating coil is disabled unless the DAT is below the minimum setpoint

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
if temperature_air_discharge > temperature_air_discharge_setpoint_min and command_coil_heat > 0:
    fail
else:
    switch mode_system:
        case 'occupied':
            minimum = flow_volumetric_air_setpoint_min
        case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied':
            minimum = 0

    if abs(flow_volumetric_air_setpoint - minimum) = 0:
        pass
    else:
        fail
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

- command_coil_heat: Heating coil command
  - Data Value Unit: percent
  - Data Point Affiliation: Terminal box control

- temperature_air_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: Terminal box monitoring

- temperature_air_discharge_setpoint_min: Minimum discharge air temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: Terminal box control
"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxDeadbandAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
        "command_coil_heat",
        "temperature_air_discharge",
        "temperature_air_discharge_setpoint_min",
    ]

    def setpoint_at_minimum(
        self,
        mode_system,
        state_zone,
        v_min,
        v_sp,
        cmd_coil_heat,
        t_discharge,
        t_discharge_min_sp,
    ):
        if state_zone.lower().strip() != "deadband":
            return "Untested"
        if (
            t_discharge
            > t_discharge_min_sp - self.get_tolerance("temperature", "discharge_air")
            and cmd_coil_heat > self.get_tolerance("damper", "command") * 100
        ):
            return False
        match mode_system.strip().lower():
            case "occupied":
                dbmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                dbmin = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if abs(v_sp - dbmin) <= self.get_tolerance("airflow", "general"):
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
                t["command_coil_heat"],
                t["temperature_air_discharge"],
                t["temperature_air_discharge_setpoint_min"],
            ),
            axis=1,
        )
