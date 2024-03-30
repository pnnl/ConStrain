"""
G36 2021
### Description

Section 5.5.5.1

- When the Zone State is cooling, the cooling-loop output shall be mapped to the active airflow setpoint from the minimum endpoint to the cooling maximum endpoint.

Verification Item:

- When in cooling stage, check if active airflow setpoint is within the correct setpoint boundary values.

### Verification logic

```
switch operation_mode
case 'occupied'
    cooling_maximum = v_cool_max
    minimum = v_min
case 'cooldown', 'setup'
    cooling_maximum = v_cool_max
    minimum = 0
case 'warmup', 'setback', 'unoccupied'
    cooling_maximum = 0
    minimum = 0

if minimum <= v_spt <= cooling_maximum
    pass
else
    fail
end
```

### Data requirements

- operation_mode: System operation mode
- zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
- v_cool_max: Maximum cooling airflow setpoint
- v_min: Occupied zone minimum airflow setpoint
- v_spt: Active airflow setpoint

"""

from constrain.checklib import RuleCheckBase
import numpy as np


class G36CoolingOnlyTerminalBoxCoolingAirflowSetpoint(RuleCheckBase):
    points = ["operation_mode", "zone_state", "v_cool_max", "v_min", "v_spt"]

    def setpoint_in_range(self, operation_mode, zone_state, v_cool_max, v_min, v_spt):
        if zone_state.lower().strip() != "cooling":
            return np.nan
        match operation_mode.strip().lower():
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
                return np.nan

        if cooling_minimum <= v_spt <= cooling_maximum:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_in_range(
                t["operation_mode"],
                t["zone_state"],
                t["v_cool_max"],
                t["v_min"],
                t["v_spt"],
            ),
            axis=1,
        )
