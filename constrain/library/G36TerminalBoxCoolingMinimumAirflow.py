"""
### Description

This verification aims to check if the terminal box maintains appropriate minimum airflow setpoints during cooling operation. When supply air is warmer than room temperature, the airflow should be limited to prevent unnecessary heating.

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
if ahu_sat_spt <= room_temp:
    untested
else:
    match operation_mode:
        case 'occupied':
            minimum = v_min
        case 'cooldown' | 'setup' | 'warmup' | 'setback' | 'unoccupied':
            minimum = 0

    if v_spt - v_spt_tol > minimum:
        fail
    else:
        pass
```

### Data requirements

- operation_mode: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: Current system operation mode
  - Data Point Affiliation: System control

- zone_state: Zone state
  - Data Value Unit: enumeration
  - Data point Description: Current zone state (heating, cooling, or deadband)
  - Data Point Affiliation: Zone control

- v_min: Minimum airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Occupied zone minimum airflow setpoint
  - Data Point Affiliation: Zone airflow control

- ahu_sat_spt: Supply air temperature setpoint
  - Data Value Unit: °C
  - Data point Description: AHU supply air temperature setpoint
  - Data Point Affiliation: AHU control

- v_spt: Active airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current active airflow setpoint
  - Data Point Affiliation: Zone airflow control

- v_spt_tol: Airflow tolerance
  - Data Value Unit: volumetric flow rate
  - Data point Description: Allowable deviation from setpoint
  - Data Point Affiliation: Zone airflow control

- room_temp: Room temperature
  - Data Value Unit: °C
  - Data point Description: Current zone air temperature
  - Data Point Affiliation: Zone monitoring

"""

from constrain.checklib import RuleCheckBase


class G36TerminalBoxCoolingMinimumAirflow(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_min",
        "ahu_sat_spt",
        "v_spt",
        "v_spt_tol",
        "room_temp",
    ]

    def setpoint_at_minimum_when_dat_high(
        self,
        operation_mode,
        zone_state,
        v_min,
        ahu_sat_spt,
        v_spt,
        v_spt_tol,
        room_temp,
    ):
        if zone_state.lower().strip() != "cooling":
            return "Untested"
        if ahu_sat_spt <= room_temp:
            return "Untested"
        match operation_mode.strip().lower():
            case "occupied":
                airflowmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                airflowmin = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if v_spt - v_spt_tol > airflowmin:
            return False
        else:
            return True

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_at_minimum_when_dat_high(
                t["operation_mode"],
                t["zone_state"],
                t["v_min"],
                t["ahu_sat_spt"],
                t["v_spt"],
                t["v_spt_tol"],
                t["room_temp"],
            ),
            axis=1,
        )
