"""
### Description

Section 5.16.12.1.
- If the supply air temperature drops below 4.4°C (40°F) for 5 minutes, send two (or more, as required to ensure that heating plant is active) heating hot-water plant requests, override the outdoor air damper to the minimum position, and modulate the heating coil to maintain a supply air temperature of at least 6°C (42°F). Disable this function when supply air temperature rises above 7°C (45°F) for 5 minutes.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.12 Freeze Protection
- Code Subsection: 5.16.12.1 Stage 1

### Verification Approach

The verification monitors supply air temperature and outdoor air damper position. When temperature drops below 4.4°C (40°F) for 5 minutes, it verifies that the outdoor air damper moves to minimum position. The protection should remain active until temperature rises above 7°C (45°F) for 5 minutes.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units
- Climate Zone(s): any
- Component(s): supply air temperature sensors, outdoor air dampers

### Verification Algorithm Pseudo Code

```python
if temperature_air_supply_setpoint < 4.4 (continuously 5 minutes) and position_damper_air_outdoor > position_damper_air_outdoor_min:
    fail
elif position_damper_air_outdoor > position_damper_air_outdoor_min and not (temperature_air_supply_setpoint > 7 (continuously 5 minutes)):
    fail
else:
    pass

if never (temperature_air_supply_setpoint < 4.4 (continuously 5 minutes)):
    untested
```

### Data requirements

- temperature_air_supply_setpoint: Supply air temperature setpoint
  - Data Value Unit: °C
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_outdoor_min: Minimum outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

"""

from constrain.checklib import RuleCheckBase


class G36FreezeProtectionStage1(RuleCheckBase):
    points = [
        "temperature_air_supply_setpoint",
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_min",
    ]

    def ts_verify_logic(self, t):
        if not t["freeze_status"]:
            return True
        if (t["sat_lowerthan_4.4_timer"] > 5) and (
            t["position_damper_air_outdoor"]
            > t["position_damper_air_outdoor_min"]
            - self.get_tolerance("damper", "position")
        ):
            return False
        elif (
            t["position_damper_air_outdoor"]
            > t["position_damper_air_outdoor_min"]
            - self.get_tolerance("damper", "position")
        ) and (not (t["sat_higherthan_7_timer"] >= 5)):
            return False
        else:
            return True

    def add_timers(self):
        lt4p4_timer_list = []
        ht7_timer_list = []
        freeze_status_list = []
        lt4p4_timer_start = None
        ht7_timer_start = None
        freeze_status = False
        for i, t in self.df.iterrows():
            if t["temperature_air_supply_setpoint"] < (
                4.4 + self.get_tolerance("temperature", "supply_air")
            ):
                if lt4p4_timer_start is None:
                    lt4p4_timer_start = i
                    lt4p4_timer_list.append(0)
                else:
                    time_delta = (i - lt4p4_timer_start).total_seconds() / 60
                    lt4p4_timer_list.append(time_delta)
                    if time_delta > 5:
                        freeze_status = True
            else:
                lt4p4_timer_start = None
                lt4p4_timer_list.append(0)

            if t["temperature_air_supply_setpoint"] > (
                7 - self.get_tolerance("temperature", "supply_air")
            ):
                if ht7_timer_start is None:
                    ht7_timer_start = i
                    ht7_timer_list.append(0)
                else:
                    time_delta = (i - ht7_timer_start).total_seconds() / 60
                    ht7_timer_list.append(time_delta)
                    if time_delta >= 5:
                        freeze_status = False
            else:
                ht7_timer_start = None
                ht7_timer_list.append(0)

            freeze_status_list.append(freeze_status)

        self.df["sat_lowerthan_4.4_timer"] = lt4p4_timer_list
        self.df["sat_higherthan_7_timer"] = ht7_timer_list
        self.df["freeze_status"] = freeze_status_list

    def verify(self):
        self.add_timers()
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if self.df["sat_lowerthan_4.4_timer"].max() <= 5:
                return "Untested"
            else:
                return True
