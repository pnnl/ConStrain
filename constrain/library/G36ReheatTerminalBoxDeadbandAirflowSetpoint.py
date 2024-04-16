"""
G36 2021
### Description

Section 5.6.5.2

- When the Zone State is deadband, the active airflow setpoint shall be the minimum endpoint. Heating coil is disabled unless the DAT is below the minimum setpoint

### Verification logic

```
if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol
    fail
else
   switch operation_mode
   case 'occupied'
       minimum = v_min
   case 'cooldown', 'setup', 'warmup', 'setback', 'unoccupied'
       minimum = 0
   if abs(v_spt - minimum) <= v_spt_tol
       pass
   else
       fail
end
```

### Data requirements

- operation_mode: System operation mode
- zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
- v_min: Occupied zone minimum airflow setpoint
- v_spt: Active airflow setpoint
- v_spt_tol: Airflow setpoint tolerance
- heating_coil_command: Heating coil command
- heating_coil_command_tol: Heating coil command saturation tolerance
- dat: Discharge air temperature
- dat_min_spt: Minimum discharge air temperature setpoint

"""

from constrain.checklib import RuleCheckBase
import numpy as np


class G36ReheatTerminalBoxDeadbandAirflowSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_min",
        "v_spt",
        "v_spt_tol",
        "heating_coil_command",
        "heating_coil_command_tol",
        "dat",
        "dat_min_spt",
    ]

    def setpoint_at_minimum(
        self,
        operation_mode,
        zone_state,
        v_min,
        v_spt,
        v_spt_tol,
        heating_coil_command,
        heating_coil_command_tol,
        dat,
        dat_min_spt,
    ):
        if zone_state.lower().strip() != "deadband":
            return np.nan
        if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol:
            return False
        match operation_mode.strip().lower():
            case "occupied":
                dbmin = v_min
            case "cooldown" | "setup" | "warmup" | "setback" | "unoccupied":
                dbmin = 0
            case _:
                print("invalid operation mode value")
                return np.nan

        if abs(v_spt - dbmin) <= v_spt_tol:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.setpoint_at_minimum(
                t["operation_mode"],
                t["zone_state"],
                t["v_min"],
                t["v_spt"],
                t["v_spt_tol"],
                t["heating_coil_command"],
                t["heating_coil_command_tol"],
                t["dat"],
                t["dat_min_spt"],
            ),
            axis=1,
        )
