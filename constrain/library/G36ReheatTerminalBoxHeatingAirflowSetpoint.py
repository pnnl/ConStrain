"""
### Description

This verification aims to check if the terminal box with reheat operates correctly when the zone is in heating mode. The control sequence involves two stages based on heating loop output: first adjusting discharge temperature while maintaining minimum airflow, then increasing airflow if more heating is needed.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.6.5 Terminal Box Airflow Control with Reheat
- Code Subsection: 5.6.5.3 (a, b) Heating Airflow Control

### Verification Approach

The verification checks the control sequence in two stages:
1. For heating loop output 0-50%:
   - Airflow should be at heating minimum
   - Discharge temperature setpoint should be within limits
2. For heating loop output 51-100%:
   - If discharge air is warm enough, airflow should modulate between min and max
   - Airflow limits vary by operation mode

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV terminal boxes with reheat
- Climate Zone(s): any
- Component(s): terminal box controllers, airflow sensors, heating coils

### Verification Algorithm Pseudo Code

```python
switch mode_system:
    case 'occupied':
        heating_maximum = max(v_heat_min, v_min)
        heating_minimum = max(v_heat_min, v_min)
    case 'cooldown':
        heating_maximum = v_heat_max
        heating_minimum = v_heat_min
    case 'setup', 'unoccupied':
        heating_maximum = 0
        heating_minimum = 0
    case 'warmup', 'setback':
        heating_maximum = v_heat_max
        heating_minimum = v_cool_max

if 0 < signal_heat <= 50:
    if abs(v_sp - heating_minimum) <= tol_v and t_sa_sp <= t_discharge_sp <= 11 + t_space_sp:
        pass
    else:
        fail
elif 50 < signal_heat <= 100:
    if t_discharge > t_room + 3 and heating_minimum <= v_sp <= heating_maximum:
        pass
    else:
        untested
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

- v_cool_max: Maximum cooling airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Maximum cooling airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_heat_max: Maximum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Maximum heating airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_heat_min: Minimum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum heating airflow setpoint
  - Data Point Affiliation: Zone airflow control

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

- signal_heat: Zone heating loop signal
  - Data Value Unit: percent
  - Data point Description: Zone heating loop signal (0-100)
  - Data Point Affiliation: Zone temperature control

- t_room: Room temperature
  - Data Value Unit: temperature
  - Data point Description: Room temperature
  - Data Point Affiliation: Zone monitoring

- t_space_sp: Space temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Space temperature setpoint
  - Data Point Affiliation: Zone control

- t_sa_sp: Supply air temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Supply air temperature setpoint
  - Data Point Affiliation: AHU control

- t_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data point Description: Discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

- t_discharge_sp: Discharge air temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Discharge air temperature setpoint
  - Data Point Affiliation: Terminal box control

"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxHeatingAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_cool_max",
        "flow_volumetric_air_heat_max",
        "flow_volumetric_air_heat_min",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
        "signal_heat",
        "temperature_air_room",
        "temperature_air_space_setpoint",
        "temperature_air_supply",
        "temperature_air_discharge",
        "temperature_air_discharge_setpoint",
    ]

    def setpoint_in_range(
        self,
        mode_system,
        state_zone,
        v_cool_max,
        v_heat_max,
        v_heat_min,
        v_min,
        v_sp,
        tol_v,
        signal_heat,
        t_room,
        t_space_sp,
        t_sa_sp,
        t_discharge,
        t_discharge_sp,
    ):
        if state_zone.lower().strip() != "heating":
            return "Untested"

        match mode_system.strip().lower():
            case "occupied":
                heating_max = max(v_heat_min, v_min)
                heating_min = max(v_heat_min, v_min)
            case "cooldown":
                heating_max = v_heat_max
                heating_min = v_heat_min
            case "setup" | "unoccupied":
                heating_max = 0
                heating_min = 0
            case "warmup" | "setback":
                heating_max = v_heat_max
                heating_min = v_cool_max
            case _:
                print("invalid operation mode value")
                return "Untested"

        if 0 < signal_heat <= 50:
            if (
                abs(v_sp - heating_min) <= tol_v
                and t_sa_sp <= t_discharge_sp <= 11 + t_space_sp
            ):
                return True
            else:
                return False

        if 50 < signal_heat <= 100:
            if t_discharge > t_room + 3 and heating_min <= v_sp <= heating_max:
                return True
            else:
                return "Untested"

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["mode_system"],
                t["state_zone"],
                t["flow_volumetric_air_cool_max"],
                t["flow_volumetric_air_heat_max"],
                t["flow_volumetric_air_heat_min"],
                t["flow_volumetric_air_setpoint_min"],
                t["flow_volumetric_air_setpoint"],
                self.get_tolerance("airflow", "general"),
                t["signal_heat"],
                t["temperature_air_room"],
                t["temperature_air_space_setpoint"],
                t["temperature_air_supply"],
                t["temperature_air_discharge"],
                t["temperature_air_discharge_setpoint"],
            ),
            axis=1,
        )
