"""
G36 2021
### Description

Section 5.5.5.3

- When the Zone State is heating, the Heating Loop output shall be mapped to the active airflow setpoint from the minimum endpoint to the heating maximum endpoint.

Verification Item:

- When in heating stage, check if active airflow setpoint is within the correct setpoint boundary values.

### Verification logic

```
switch operation_mode
case 'occupied'
    heating_maximum = v_heat_max
    minimum = v_min
case 'cooldown', 'setup', 'unoccupied'
    heating_maximum = 0
    minimum = 0
case 'warmup', 'setback'
    heating_maximum = v_cool_max
    minimum = 0

if minimum <= v_spt <= heating_maximum
    pass
else
    fail
end
```

### Data requirements

- operation_mode: System operation mode
- zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
- v_cool_max: Zone maximum cooling airflow setpoint
- v_heat_max: Zone maximum heating airflow setpoint
- v_min: Occupied zone minimum airflow setpoint
- v_spt: Active airflow setpoint

"""

from constrain.checklib import RuleCheckBase
import numpy as np


class G36CoolingOnlyTerminalBoxHeatingAirflowSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_cool_max",
        "v_heat_max",
        "v_min",
        "v_spt",
    ]

    def setpoint_in_range(
        self, operation_mode, zone_state, v_cool_max, v_heat_max, v_min, v_spt
    ):
        if zone_state.lower().strip() != "heating":
            return np.nan
        match operation_mode.strip().lower():
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
                return np.nan

        if heating_min <= v_spt <= heating_max:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["operation_mode"],
                t["zone_state"],
                t["v_cool_max"],
                t["v_heat_max"],
                t["v_min"],
                t["v_spt"],
            ),
            axis=1,
        )
