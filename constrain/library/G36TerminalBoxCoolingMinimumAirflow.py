"""
### Description

Section 5.5.5.1.a and Section 5.6.5.1.a
- If supply air temperature from the air handler is greater than room temperature, the active airflow setpoint shall be no higher than the minimum endpoint.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.5.5 and 5.6.5 Terminal Box Control
- Code Subsection: 5.5.5.1.a and 5.6.5.1.a Cooling Airflow Control

### Verification Approach

The verification checks that when supply air temperature is above room temperature:
1. During occupied mode: airflow setpoint should not exceed minimum occupied airflow
2. During other modes: airflow setpoint should not exceed zero
The test is considered untested if supply air temperature is not above room temperature.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV terminal boxes
- Climate Zone(s): any
- Component(s): terminal box controllers, airflow sensors, temperature sensors

### Verification Algorithm Pseudo Code

```python
if temperature_air_supply_setpoint <= temperature_air_room:
    untested
else:
    match mode_system:
        case 'occupied':
            minimum = flow_volumetric_air_setpoint_min
        case 'cooldown' | 'setup' | 'warmup' | 'setback' | 'unoccupied':
            minimum = 0

    if flow_volumetric_air_setpoint > minimum:
        fail
    else:
        pass
```

### Data requirements

- mode_system: System operation mode (occupied, cooldown, setup, warmup, setback, unoccupied)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- state_zone: Zone state (if state_zone is not "cooling", this verification item falls into the "untested" result)
  - Data Value Unit: enumeration
  - Data Point Affiliation: Zone control

- flow_volumetric_air_setpoint_min: Minimum airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- temperature_air_supply_setpoint: Supply air temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: AHU control

- flow_volumetric_air_setpoint: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- temperature_air_room: Room temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: Zone monitoring
  
"""

from constrain.checklib import RuleCheckBase


class G36TerminalBoxCoolingMinimumAirflow(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_setpoint_min",
        "temperature_air_supply_setpoint",
        "flow_volumetric_air_setpoint",
        "temperature_air_room",
    ]

    def setpoint_at_minimum_when_dat_high(
        self,
        mode_system,
        state_zone,
        v_min,
        t_sa_sp,
        v_sp,
        t_room,
    ):
        if state_zone.lower().strip() != "cooling":
            return "Untested"
        if t_sa_sp <= t_room + self.get_tolerance("temperature", "general"):
            return "Untested"
        match mode_system.strip().lower():
            case "occupied":
                airflowmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                airflowmin = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if v_sp - self.get_tolerance("airflow", "general") > airflowmin:
            return False
        else:
            return True

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_at_minimum_when_dat_high(
                t["mode_system"],
                t["state_zone"],
                t["flow_volumetric_air_setpoint_min"],
                t["temperature_air_supply_setpoint"],
                t["flow_volumetric_air_setpoint"],
                t["temperature_air_room"],
            ),
            axis=1,
        )
