"""
G36 2021
### Description

Section 5.5.5.1.a and Section 5.6.5.1.a

- If supply air temperature from the air handler is greater than room temperature, the active airflow setpoint shall be no higher than the minimum endpoint.

### Verification logic

```
if ahu_sat_spt <= room_temp:
    untested
else:
    switch operation_mode
        case 'occupied'
            minimum = v_min
        case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied'
            minimum = 0
    if v_spt - v_spt_tol > minimum:
        fail
    else:
        pass
```

### Data requirements

- operation_mode: System operation mode
- zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
- v_min: Occupied zone minimum airflow setpoint
- ahu_sat_spt: AHU supply air temperature setpoint
- v_spt: Active airflow setpoint
- v_spt_tol: Airflow setpoint tolerance
- room_temp: Room temperature

"""

from constrain.checklib import RuleCheckBase
import numpy as np


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
            return np.nan
        if ahu_sat_spt <= room_temp:
            return np.nan
        match operation_mode.strip().lower():
            case "occupied":
                airflowmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                airflowmin = 0
            case _:
                print("invalid operation mode value")
                return np.nan

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
