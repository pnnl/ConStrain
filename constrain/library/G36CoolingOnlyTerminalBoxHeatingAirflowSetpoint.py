"""
### Description

Section 5.5.5.3
- When the Zone State is heating, the Heating Loop output shall be mapped to the active airflow setpoint from the minimum endpoint to the heating maximum endpoint.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.5.5 Terminal Box Airflow Control
- Code Subsection: 5.5.5.3 Heating Airflow Control

### Verification Approach

The verification checks that when the zone is in heating mode, the active airflow setpoint stays within appropriate boundaries based on the current operation mode. The boundaries vary depending on whether the system is in occupied, cooldown/setup/unoccupied, or warmup/setback mode.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV cooling-only terminal boxes
- Climate Zone(s): any
- Component(s): terminal box controllers, airflow sensors

### Verification Algorithm Pseudo Code

```
switch mode_system
case 'occupied'
    heating_maximum = flow_volumetric_air_heat_max
    minimum = flow_volumetric_air_setpoint_min
case 'cooldown', 'setup', 'unoccupied'
    heating_maximum = 0
    minimum = 0
case 'warmup', 'setback'
    heating_maximum = flow_volumetric_air_cool_max
    minimum = 0

if minimum <= flow_volumetric_air_setpoint <= heating_maximum
    pass
else
    fail
end
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

- flow_volumetric_air_setpoint_min: Minimum airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

- flow_volumetric_air_setpoint: Airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone airflow control

"""

from constrain.checklib import RuleCheckBase


class G36CoolingOnlyTerminalBoxHeatingAirflowSetpoint(RuleCheckBase):
    points = [
        "mode_system",
        "state_zone",
        "flow_volumetric_air_cool_max",
        "flow_volumetric_air_heat_max",
        "flow_volumetric_air_setpoint_min",
        "flow_volumetric_air_setpoint",
    ]

    def setpoint_in_range(
        self, mode_system, state_zone, v_cool_max, v_heat_max, v_min, v_sp
    ):
        if state_zone.lower().strip() != "heating":
            return "Untested"
        match mode_system.strip().lower():
            case "occupied":
                heating_max = v_heat_max
                heating_min = v_min
            case "cooldown" | "setup" | "unoccupied":
                heating_max = 0
                heating_min = 0
            case "warmup" | "setback":
                heating_max = v_cool_max
                heating_min = 0
            case _:
                print("invalid operation mode value")
                return "Untested"

        if heating_min <= v_sp <= heating_max:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["mode_system"],
                t["state_zone"],
                t["flow_volumetric_air_cool_max"],
                t["flow_volumetric_air_heat_max"],
                t["flow_volumetric_air_setpoint_min"],
                t["flow_volumetric_air_setpoint"],
            ),
            axis=1,
        )
