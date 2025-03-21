"""
### Description

This verification aims to check if the terminal box with reheat operates correctly when the zone is in heating mode. The control sequence involves two stages based on heating loop output: first adjusting discharge temperature while maintaining minimum airflow, then increasing airflow if more heating is needed.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.6.5 Terminal Box Airflow Control with Reheat
- Code Subsection: 5.6.5.3 Heating Airflow Control

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
switch operation_mode:
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

if 0 < heating_loop_output <= 50:
    if abs(v_spt - heating_minimum) <= tolerance and ahu_sat_spt <= dat_spt <= 11 + space_temp_spt:
        pass
    else:
        fail
elif 50 < heating_loop_output <= 100:
    if dat > room_temp + 3 and heating_minimum <= v_spt <= heating_maximum:
        pass
    else:
        untested
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
  - Data point Description: Zone maximum cooling airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_heat_max: Maximum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Zone maximum heating airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_heat_min: Minimum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Zone minimum heating airflow setpoint
  - Data Point Affiliation: Zone airflow control

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

- heating_loop_output: Heating loop signal
  - Data Value Unit: percent (0-100)
  - Data point Description: Zone heating control loop output
  - Data Point Affiliation: Zone temperature control

- room_temp: Room temperature
  - Data Value Unit: °C
  - Data point Description: Current zone air temperature
  - Data Point Affiliation: Zone monitoring

- space_temp_spt: Space temperature setpoint
  - Data Value Unit: °C
  - Data point Description: Zone temperature setpoint
  - Data Point Affiliation: Zone control

- ahu_sat_spt: Supply air temperature setpoint
  - Data Value Unit: °C
  - Data point Description: AHU supply air temperature setpoint
  - Data Point Affiliation: AHU control

- dat: Discharge air temperature
  - Data Value Unit: °C
  - Data point Description: Terminal box discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

- dat_spt: Discharge temperature setpoint
  - Data Value Unit: °C
  - Data point Description: Terminal box discharge air temperature setpoint
  - Data Point Affiliation: Terminal box control

"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxHeatingAirflowSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_cool_max",
        "v_heat_max",
        "v_heat_min",
        "v_min",
        "v_spt",
        "v_spt_tol",
        "heating_loop_output",
        "room_temp",
        "space_temp_spt",
        "ahu_sat_spt",
        "dat",
        "dat_spt",
    ]

    def setpoint_in_range(
        self,
        operation_mode,
        zone_state,
        v_cool_max,
        v_heat_max,
        v_heat_min,
        v_min,
        v_spt,
        v_spt_tol,
        heating_loop_output,
        room_temp,
        space_temp_spt,
        ahu_sat_spt,
        dat,
        dat_spt,
    ):
        if zone_state.lower().strip() != "heating":
            return "Untested"

        match operation_mode.strip().lower():
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

        if 0 < heating_loop_output <= 50:
            if (
                abs(v_spt - heating_min) <= v_spt_tol
                and ahu_sat_spt <= dat_spt <= 11 + space_temp_spt
            ):
                return True
            else:
                return False

        if 50 < heating_loop_output <= 100:
            if dat > room_temp + 3 and heating_min <= v_spt <= heating_max:
                return True
            else:
                return "Untested"

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["operation_mode"],
                t["zone_state"],
                t["v_cool_max"],
                t["v_heat_max"],
                t["v_heat_min"],
                t["v_min"],
                t["v_spt"],
                t["v_spt_tol"],
                t["heating_loop_output"],
                t["room_temp"],
                t["space_temp_spt"],
                t["ahu_sat_spt"],
                t["dat"],
                t["dat_spt"],
            ),
            axis=1,
        )
