"""
G36 2021
### Description

Section 5.6.5.3

- When the Zone State is heating, the Heating Loop shall maintain space temperature at the heating setpoint as follows:

    - a. From 0% to 50%, the heating-loop output shall reset the discharge temperature setpoint from the current AHU SAT setpoint to a maximum of Max Delta T above space temperature setpoint. The active airflow setpoint shall be the heating minimum endpoint.
    - b. From 51% to 100%, if the DAT is greater than room temperature plus 3°C (5°F), the heating-loop output shall reset the active airflow setpoint from the heating minimum endpoint to the heating maximum endpoint.

### Verification logic

```
switch operation_mode
    case 'occupied'
        heating_maximum = max(v_heat_min, v_min)
        heating_minimum = max(v_heat_min, v_min)
    case 'cooldown'
        heating_maximum = v_heat_max
        heating_minimum = v_heat_min
    case 'setup', 'unoccupied'
        heating_maximum = 0
        heating_minimum = 0
    case 'warmup', 'setback'
        heating_maximum = v_heat_max
        heating_minimum = v_cool_max

    if 0 < heating_loop_output <= 50:
        if abs(v_spt - heating_minimum) <= tolerance and ahu_sat_spt <= dat_spt <= 11 + space_temp_spt:
            pass
        else:
            fail
    if 50 < heating_loop_output <= 100:
        if dat > room_temp + 3 and heating_minimum <= v_spt <= heating_maximum:
            pass
        else:
            untested
    end
```

### Data requirements

- operation_mode: System operation mode
- zone_state: Zone state (heating, cooling, or deadband (not in either heating or cooling))
- v_cool_max: Zone maximum cooling airflow setpoint
- v_heat_max: Zone maximum heating airflow setpoint
- v_heat_min: "Zone minimum heating airflow setpoint
- v_min: Occupied zone minimum airflow setpoint
- v_spt: Active airflow setpoint
- v_spt_tol: Airflow setpoint tolerance
- heating_loop_output: Zone heating loop signal (from 0 to 100)
- room_temp: Room temperature
- space_temp_spt: Space temperature setpoint
- ahu_sat_spt: AHU supply air temperature setpoint
- dat: Discharge air temperature
- dat_spt: Discharge air temperature setpoint

"""

from constrain.checklib import RuleCheckBase
import numpy as np


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
            return np.nan

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
                return np.nan

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
                return np.nan

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
