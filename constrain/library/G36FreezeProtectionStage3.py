"""
### Description

This verification aims to check if the third (highest) stage of freeze protection control operates correctly. When severe freezing conditions are detected, the system should shut down fans, close outdoor air dampers, and adjust coil valves to prevent damage.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.12 Freeze Protection
- Code Subsection: 5.16.12.3 Stage 3 (Highest)

### Verification Approach

The verification monitors multiple conditions that can trigger stage 3 protection: freeze-stat signal, sustained low temperatures, or critically low temperatures. When triggered, it verifies that fans are stopped, dampers are closed, and coils are properly positioned to prevent freezing damage.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units
- Climate Zone(s): any
- Component(s): supply air temperature sensors, freeze-stats, fans, dampers, coils

### Verification Algorithm Pseudo Code

```python
if supply_air_temp < 3.3 (continuously 15 minutes) or
  supply_air_temp < 1 (continuously 5 minutes) or
  freeze_stat == True:
    if not (
        outdoor_damper_command == 0 and
        supply_fan_status == 'off' and
        return_fan_status == 'off' and
        relief_fan_status == 'off' and
        cooling_coil_command == 100 and
        heating_coil_command > 0
    ):
        fail
    else:
        pass

if never (
    supply_air_temp < 3.3 (continuously 15 minutes) or
    supply_air_temp < 1 (continuously 5 minutes) or
    freeze_stat == True
):
    untested
```

### Data requirements

- freeze_stat: Freeze-stat status
  - Data Value Unit: binary
  - Data point Description: Status of freeze protection thermostat (optional)
  - Data Point Affiliation: Air handling unit

- supply_air_temp: Supply air temperature
  - Data Value Unit: °C
  - Data point Description: Temperature of supply air downstream of cooling coil
  - Data Point Affiliation: Air handling unit

- outdoor_damper_command: Outdoor air damper position
  - Data Value Unit: fraction (0-1)
  - Data point Description: Current position command to outdoor air damper
  - Data Point Affiliation: Air handling unit

- supply_fan_status: Supply fan status
  - Data Value Unit: binary
  - Data point Description: Operating status of supply fan
  - Data Point Affiliation: Air handling unit

- return_fan_status: Return fan status
  - Data Value Unit: binary
  - Data point Description: Operating status of return fan (optional)
  - Data Point Affiliation: Air handling unit

- relief_fan_status: Relief fan status
  - Data Value Unit: binary
  - Data point Description: Operating status of relief fan (optional)
  - Data Point Affiliation: Air handling unit

- cooling_coil_command: Cooling coil valve position
  - Data Value Unit: percent (0-100)
  - Data point Description: Position command to cooling coil valve
  - Data Point Affiliation: Air handling unit

- heating_coil_command: Heating coil valve position
  - Data Value Unit: percent (0-100)
  - Data point Description: Position command to heating coil valve
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36FreezeProtectionStage3(RuleCheckBase):
    points = [
        "freeze_stat",
        "supply_air_temp",
        "outdoor_damper_command",
        "supply_fan_status",
        "return_fan_status",
        "relief_fan_status",
        "cooling_coil_command",
        "heating_coil_command",
    ]

    def ts_verify_logic(self, t):
        if not (t["freeze_status"] or bool(t["freeze_stat"])):
            return True
        if (
            (t["sat_lowerthan_3.3_timer"] > 15)
            or (t["sat_lowerthan_1_timer"] > 5)
            or t["freeze_stat"]
        ):
            if not (
                t["outdoor_damper_command"] < 1
                and (not bool(t["supply_fan_status"]))
                and (not bool(t["return_fan_status"]))
                and (not bool(t["relief_fan_status"]))
                and t["cooling_coil_command"] > 99
                and t["heating_coil_command"] > 0
            ):
                return False
        return True

    def add_timers(self):
        lt3p3_timer_list = []
        lt1_timer_list = []
        freeze_status_list = []
        lt3p3_timer_start = None
        lt1_timer_start = None
        freeze_status = False
        for i, t in self.df.iterrows():
            if t["supply_air_temp"] < 3.3:
                if lt3p3_timer_start is None:
                    lt3p3_timer_start = i
                    lt3p3_timer_list.append(0)
                    freeze_status = False  # add with discretionary interpretation
                else:
                    time_delta = (i - lt3p3_timer_start).total_seconds() / 60
                    lt3p3_timer_list.append(time_delta)
                    if time_delta > 15:
                        freeze_status = True
            else:
                lt3p3_timer_start = None
                lt3p3_timer_list.append(0)

            if t["supply_air_temp"] < 1:
                if lt1_timer_start is None:
                    lt1_timer_start = i
                    lt1_timer_list.append(0)
                else:
                    time_delta = (i - lt1_timer_start).total_seconds() / 60
                    lt1_timer_list.append(time_delta)
                    if time_delta > 5:
                        freeze_status = True
            else:
                lt1_timer_start = None
                lt1_timer_list.append(0)

            freeze_status_list.append(freeze_status)

        self.df["sat_lowerthan_3.3_timer"] = lt3p3_timer_list
        self.df["sat_lowerthan_1_timer"] = lt1_timer_list
        self.df["freeze_status"] = freeze_status_list

    def verify(self):
        self.add_timers()
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        free_stat_bool_list = [bool(x) for x in self.df["freeze_stat"]]
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if self.df["freeze_status"].any() or (True in free_stat_bool_list):
                return True
            else:
                return "Untested"
