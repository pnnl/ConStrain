"""
### Description

Section 5.6.5.1
- When the Zone State is cooling, the cooling-loop output shall be mapped to the active airflow setpoint from the cooling minimum endpoint to the cooling maximum endpoint. Heating coil is disabled unless the DAT is below the minimum setpoint

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.6.5 Terminal Box Airflow Control with Reheat
- Code Subsection: 5.6.5.1 Cooling Airflow Control

### Verification Approach

The verification checks two conditions:
1. When discharge air temperature is above minimum setpoint, heating coil should remain off
2. Active airflow setpoint should stay within appropriate boundaries based on operation mode

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
            cooling_maximum = flow_volumetric_air_cool_max
            minimum = flow_volumetric_air_setpoint_min
        case 'cooldown', 'setup':
            cooling_maximum = flow_volumetric_air_cool_max
            minimum = 0
        case 'warmup', 'setback', 'unoccupied':
            cooling_maximum = 0
            minimum = 0

    if cooling_minimum <= flow_volumetric_air_setpoint <= cooling_maximum:
        pass
    else:
        fail
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


class G36ReheatTerminalBoxCoolingAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_cool_max",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
        "command_coil_heat",
        "temperature_air_discharge",
        "temperature_air_discharge_setpoint_min",
    ]

    def setpoint_in_range(
        self,
        mode_system,
        state_zone,
        v_cool_max,
        v_min,
        v_sp,
        cmd_coil_heat,
        tol_cmd_coil_heat,
        t_discharge,
        t_discharge_min_sp,
    ):
        if state_zone.lower().strip() != "cooling":
            return "Untested"
        if t_discharge > t_discharge_min_sp and cmd_coil_heat > tol_cmd_coil_heat:
            return False
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
                t["command_coil_heat"],
                self.get_tolerance("coil", "command"),
                t["temperature_air_discharge"],
                t["temperature_air_discharge_setpoint_min"],
            ),
            axis=1,
        )
