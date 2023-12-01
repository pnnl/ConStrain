"""
G36 2021

### Description

5.16.12.3.	Upon signal from the freeze-stat (if installed), or if supply air temperature drops below 3.3°C (38°F) for 15 minutes or below 1°C (34°F) for 5 minutes, shut down supply and return/relief fan(s), close outdoor air damper, open the cooling-coil valve to 100%, and energize the CHW pump system. Also send two (or more, as required to ensure that heating plant is active) heating hot-water plant requests, modulate the heating coil to maintain the higher of the supply air temperature or the mixed air temperature at 27°C (80°F), and set a Level 2 alarm indicating the unit is shut down by freeze protection.

### Verification logic

```python
if supply_air_temp < 3.3 (continuously 15 minutes) or
  supply_air_temp < 1 (continuously 5 minutes) or
  freeze_stat == True
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

- freeze_stat: (optional, set to False if system does not have it) binary freeze-stat
- supply_air_temp: supply air temperature
- outdoor_damper_command: outdoor air damper
- supply_fan_status: supply fan status (speed): [1, 0] (can be replaced by binary or numeric variables)
- return_fan_status: (optional, set to False if system does not have it) return fan status (speed)
- relief_fan_status: (optional, set to False if system does not have it) relief fan status (speed)
- cooling_coil_command: cooling coil command
- heating_coil_command: heating coil command
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
