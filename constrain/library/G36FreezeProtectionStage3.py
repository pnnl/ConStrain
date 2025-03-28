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
if t_sa < 3.3 (continuously 15 minutes) or
  t_sa < 1 (continuously 5 minutes) or
  flag_freeze == True:
    if not (
        pos_damper_oa == 0 and
        status_fan_supply == 'off' and
        status_fan_return == 'off' and
        status_fan_relief == 'off' and
        cmd_coil_cool == 100 and
        cmd_coil_heat > 0
    ):
        fail
    else:
        pass

if never (
    t_sa < 3.3 (continuously 15 minutes) or
    t_sa < 1 (continuously 5 minutes) or
    flag_freeze == True
):
    untested
```

### Data requirements

- flag_freeze: Freeze protection flag
  - Data Value Unit: binary
  - Data point Description: Freeze protection flag
  - Data Point Affiliation: Air handling unit

- t_sa: Supply air temperature
  - Data Value Unit: °C
  - Data point Description: Supply air temperature
  - Data Point Affiliation: Air handling unit

- pos_damper_oa: Outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper command
  - Data Point Affiliation: Air handling unit

- status_fan_supply: Supply fan status
  - Data Value Unit: binary
  - Data point Description: Supply fan status
  - Data Point Affiliation: Air handling unit

- status_fan_return: Return fan status
  - Data Value Unit: binary
  - Data point Description: Return fan status
  - Data Point Affiliation: Air handling unit

- status_fan_relief: Relief fan status
  - Data Value Unit: binary
  - Data point Description: Relief fan status
  - Data Point Affiliation: Air handling unit

- cmd_coil_cool: Cooling valve command
  - Data Value Unit: percent
  - Data point Description: Cooling valve command
  - Data Point Affiliation: Air handling unit

- cmd_coil_heat: Heating valve command
  - Data Value Unit: percent
  - Data point Description: Heating valve command
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36FreezeProtectionStage3(RuleCheckBase):
    points = [
        "status_freeze",
        "temperature_air_supply",
        "position_damper_air_outdoor",
        "status_fan_supply",
        "status_fan_return",
        "status_fan_relief",
        "command_coil_cool",
        "command_coil_heat",
    ]

    def ts_verify_logic(self, t):
        if not (t["freeze_status"] or bool(t["status_freeze"])):
            return True
        if (
            (t["sat_lowerthan_3.3_timer"] > 15)
            or (t["sat_lowerthan_1_timer"] > 5)
            or t["status_freeze"]
        ):
            if not (
                t["position_damper_air_outdoor"]
                < self.get_tolerance("damper", "command")
                and (not bool(t["status_fan_supply"]))
                and (not bool(t["status_fan_return"]))
                and (not bool(t["status_fan_relief"]))
                and t["command_coil_cool"]
                >= 100 - self.get_tolerance("damper", "command") * 100
                and t["command_coil_heat"] > 0
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
            if t["temperature_air_supply"] < (
                3.3 - self.get_tolerance("temperature", "supply_air")
            ):
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

            if t["temperature_air_supply"] < (
                1 - self.get_tolerance("temperature", "supply_air")
            ):
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
        free_stat_bool_list = [bool(x) for x in self.df["status_freeze"]]
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if self.df["freeze_status"].any() or (True in free_stat_bool_list):
                return True
            else:
                return "Untested"
