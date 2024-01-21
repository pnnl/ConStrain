"""
G36 2021

### Description

Section 5.16 interpretation:

- With Relief damper or relief fan
  - when economizer control is not in lockout, and actual damper positions are controlled by the SAT control loop. Above only set the lower limit for OA damper. Track MinOAsp with a reverse-acting loop and map output to
    - OA (economizer) damper minimum position MinOA-P
    - return air damper maximum position MaxRA-P
  - when economizer is in lockout for more than 10 minutes (exceeding economizer high limit conditions in Section 5.1.17), the dampers are controlled to meet minimum OA requirements
    - fully open RA damper
    - set MaxOA-P = MinOA-P, control OA damper to meet MinOAsp
    - modulate RA damper to maintain MinOAsp (return air damper position equals to MaxRA-P)

Verification Item 2:

- when economizer condition is not okay and occupied, control dampers to maintain outdoor air flow setpoint

### Verification logic

```python
if economizer_lockout(outdoor_air_temp, economizer_high_limit_sp) and sys_mode == 'occupied':
  if outdoor_air_flow < MinOAsp (continuously (e.g. fall below the sp for a consecutive 1 hr)):
    if outdoor_damper_command == 100 and return_damper_command == 0:
      pass
    else:
      fail
  elif outdoor_air_flow > MinOAsp (continuously):
    if outdoor_damper_command == 0 and return_damper_command == 100:
      pass
    else:
      fail
  else:
    pass (essentially untested yet)
else:
  untested
```

- outdoor_air_temp: outdoor air temperature
- economizer_high_limit_sp: economizer lockout high limit set point
- outdoor_damper_command: outdoor air damper command
- return_damper_command: return air damper command
- outdoor_air_flow: outdoor air flow rate
- min_oa_sp: minimum outdoor air flow rate setpoint
- sys_mode: AHU system mode mode, enumeration of ['occupied', 'unoccupied', 'cooldown', 'warmup', 'setback', 'setup']

"""

from constrain.checklib import RuleCheckBase
import numpy as np


class G36MinOAwoEconomizer(RuleCheckBase):
    points = [
        "outdoor_air_temp",
        "economizer_high_limit_sp",
        "outdoor_damper_command",
        "return_damper_command",
        "outdoor_air_flow",
        "min_oa_sp",
        "sys_mode",
    ]

    def economizer_lockout(self, outdoor_air_temp, economizer_high_limit_sp):
        if outdoor_air_temp > economizer_high_limit_sp:
            return True
        else:
            return False

    def ts_verify_logic(self, t):
        if (
            self.economizer_lockout(
                t["outdoor_air_temp"], t["economizer_high_limit_sp"]
            )
            and t["sys_mode"].strip().lower() == "occupied"
        ):
            if t["oaf_low_timer"] > 60:
                if t["outdoor_damper_command"] > 99 and t["return_damper_command"] < 1:
                    return True
                else:
                    return False
            elif t["oaf_high_timer"] > 60:
                if t["outdoor_damper_command"] < 1 and t["return_damper_command"] > 99:
                    return True
                else:
                    return False
            else:
                return np.nan
        else:
            return np.nan

    def add_timers(self):
        low_timer_list = []
        high_timer_list = []
        low_timer_start = None
        high_timer_start = None
        for i, t in self.df.iterrows():
            if (
                self.economizer_lockout(
                    t["outdoor_air_temp"], t["economizer_high_limit_sp"]
                )
                and t["sys_mode"].strip().lower() == "occupied"
            ):
                # only count the timers when it is in occupied mode with economizer lockout
                if t["outdoor_air_flow"] < t["min_oa_sp"]:
                    high_timer_start = None
                    high_timer_list.append(0)
                    if low_timer_start is None:
                        low_timer_start = i
                        low_timer_list.append(0)
                    else:
                        low_timer_list.append(
                            (i - low_timer_start).total_seconds() / 60
                        )
                if t["outdoor_air_flow"] > t["min_oa_sp"]:
                    low_timer_start = None
                    low_timer_list.append(0)
                    if high_timer_start is None:
                        high_timer_start = i
                        high_timer_list.append(0)
                    else:
                        high_timer_list.append(
                            (i - high_timer_start).total_seconds() / 60
                        )
            else:
                # outside of the (occupied mode and economizer lockout) condition, reset counters
                high_timer_start = None
                high_timer_list.append(0)
                low_timer_start = None
                low_timer_list.append(0)

        self.df["oaf_low_timer"] = low_timer_list
        self.df["oaf_high_timer"] = high_timer_list

    def verify(self):
        self.add_timers()
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)
