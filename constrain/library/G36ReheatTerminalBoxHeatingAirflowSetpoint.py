"""
### Description

Section 5.6.5.3
- When the Zone State is heating, the Heating Loop shall maintain space temperature at the heating setpoint as follows:
    - a. From 0% to 50%, the heating-loop output shall reset the discharge temperature setpoint from the current AHU SAT setpoint to a maximum of Max Delta T above space temperature setpoint. The active airflow setpoint shall be the heating minimum endpoint.
    - b. From 51% to 100%, if the DAT is greater than room temperature plus 3°C (5°F), the heating-loop output shall reset the active airflow setpoint from the heating minimum endpoint to the heating maximum endpoint.

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
        heating_maximum = max(flow_volumetric_air_heat_min, flow_volumetric_air_setpoint_min)
        heating_minimum = max(flow_volumetric_air_heat_min, flow_volumetric_air_setpoint_min)
    case 'cooldown':
        heating_maximum = flow_volumetric_air_heat_max
        heating_minimum = flow_volumetric_air_heat_min
    case 'setup', 'unoccupied':
        heating_maximum = 0
        heating_minimum = 0
    case 'warmup', 'setback':
        heating_maximum = flow_volumetric_air_heat_max
        heating_minimum = flow_volumetric_air_cool_max

if 0 < signal_heat <= 50:
    if abs(flow_volumetric_air_setpoint - heating_minimum) = 0 and temperature_air_supply <= temperature_air_discharge_setpoint <= 11 + temperature_air_space_setpoint:
        pass
    else:
        fail
elif 50 < signal_heat <= 100:
    if temperature_air_discharge > temperature_air_room + 3 and heating_minimum <= flow_volumetric_air_setpoint <= heating_maximum:
        pass
    else:
        untested
```

### Data requirements

- mode_system: System operation mode (occupied, cooldown, setup, warmup, setback, unoccupied)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- state_zone: Zone state (if state_zone is not "heating", this verification item falls into the "untested" result)
  - Data Value Unit: enumeration
  - Data Point Affiliation: Zone control

- flow_volumetric_air_cool_max: Maximum cooling airflow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_heat_max: Maximum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_heat_min: Minimum heating airflow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_setpoint_min: Minimum airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_setpoint: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- signal_heat: Zone heating loop signal
  - Data Value Unit: percent
  - Data Point Affiliation: Zone temperature control

- temperature_air_room: Room temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: Zone monitoring

- temperature_air_space_setpoint: Space temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: Zone control

- temperature_air_supply: Supply air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: AHU control

- temperature_air_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: Terminal box monitoring

- temperature_air_discharge_setpoint: Discharge air temperature setpoint
  - Data Value Unit: temperature
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
