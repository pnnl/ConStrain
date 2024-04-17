"""
G36 2021
### Description

Section 5.6.5.1

- When the Zone State is cooling, the cooling-loop output shall be mapped to the active airflow setpoint from the cooling minimum endpoint to the cooling maximum endpoint. Heating coil is disabled unless the DAT is below the minimum setpoint

### Verification logic

```
if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol
    fail
else
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

   if cooling_minimum <= v_spt <= cooling_maximum
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
- heating_coil_command: Heating coil command
- heating_coil_command_tol: Heating coil command saturation tolerance
- dat: Discharge air temperature
- dat_min_spt: Minimum discharge air temperature setpoint

"""

from constrain.checklib import RuleCheckBase
import numpy as np


class G36ReheatTerminalBoxCoolingAirflowSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "zone_state",
        "v_cool_max",
        "v_min",
        "v_spt",
        "heating_coil_command",
        "heating_coil_command_tol",
        "dat",
        "dat_min_spt",
    ]

    def setpoint_in_range(
        self,
        operation_mode,
        zone_state,
        v_cool_max,
        v_min,
        v_spt,
        heating_coil_command,
        heating_coil_command_tol,
        dat,
        dat_min_spt,
    ):
        if zone_state.lower().strip() != "cooling":
            return np.nan
        if dat > dat_min_spt and heating_coil_command > heating_coil_command_tol:
            return False
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
                t["heating_coil_command"],
                t["heating_coil_command_tol"],
                t["dat"],
                t["dat_min_spt"],
            ),
            axis=1,
        )
