"""
### Description

Section 5.16.12.2.	
- If the supply air temperature drops below 3.3°C (38°F) for 5 minutes, fully close both the economizer damper and the minimum outdoor air damper for 1 hour and set a Level 3 alarm noting that minimum ventilation was interrupted. After 1 hour, the unit shall resume minimum outdoor air ventilation and enter the previous stage of freeze protection.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.12 Freeze Protection
- Code Subsection: 5.16.12.2 Stage 2

### Verification Approach

The verification monitors supply air temperature and outdoor air damper position. When temperature drops below 3.3°C (38°F) for 5 minutes, it verifies that both economizer and minimum outdoor air dampers are fully closed for 1 hour. After this period, the system should resume minimum ventilation.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units
- Climate Zone(s): any
- Component(s): supply air temperature sensors, outdoor air dampers

### Verification Algorithm Pseudo Code

```python
if temperature_air_supply_setpoint < 3.3 (continuously 5 minutes) and position_damper_air_outdoor > 0 (ever in the following hour):
    fail
else:
    pass

if never (temperature_air_supply_setpoint < 3.3 (continuously 5 minutes)):
    untested
```

### Data requirements

- temperature_air_supply_setpoint: Supply air temperature setpoint
  - Data Value Unit: °C
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36FreezeProtectionStage2(RuleCheckBase):
    points = ["temperature_air_supply_setpoint", "position_damper_air_outdoor"]

    def ts_verify_logic(self, t):
        if not t["freeze_status"]:
            return True
        if (t["sat_lowerthan_3.3_timer"] > 5) and (
            t["position_damper_air_outdoor"]
            > self.get_tolerance("damper", "command") * 100
        ):
            return False
        else:
            return True

    def add_timers(self):
        lt3p3_timer_list = []
        freeze_timer_list = []
        freeze_status_list = []
        lt3p3_timer_start = None
        freeze_timer_start = None
        freeze_status = False
        for i, t in self.df.iterrows():
            if t["temperature_air_supply_setpoint"] < (
                3.3 + self.get_tolerance("temperature", "supply_air")
            ):
                if lt3p3_timer_start is None:
                    lt3p3_timer_start = i
                    lt3p3_timer_list.append(0)
                else:
                    time_delta = (i - lt3p3_timer_start).total_seconds() / 60
                    lt3p3_timer_list.append(time_delta)
                    if time_delta > 5:
                        freeze_status = True
            else:
                lt3p3_timer_start = None
                lt3p3_timer_list.append(0)

            if freeze_status:
                if freeze_timer_start is None:
                    freeze_timer_start = i
                    freeze_timer_list.append(0)
                else:
                    time_delta = (i - freeze_timer_start).total_seconds() / 60
                    freeze_timer_list.append(time_delta)
                    if time_delta >= 60:
                        # reset
                        freeze_status = False
                        lt3p3_timer_start = None
                        freeze_timer_start = None

            freeze_status_list.append(freeze_status)

        self.df["sat_lowerthan_3.3_timer"] = lt3p3_timer_list
        self.df["freeze_status"] = freeze_status_list

    def verify(self):
        self.add_timers()
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if self.df["sat_lowerthan_3.3_timer"].max() <= 5:
                return "Untested"
            else:
                return True
