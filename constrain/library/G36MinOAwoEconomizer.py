"""
### Description

This verification aims to check if the minimum outdoor air control operates correctly when the economizer is in lockout. The system should modulate dampers to maintain minimum outdoor air requirements without attempting free cooling.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16 Air Handling Unit and Relief Fan Control Sequences
- Code Subsection: Minimum Outdoor Air Control without Economizer

### Verification Approach

The verification checks that during occupied periods when economizer is in lockout, the dampers are controlled to maintain minimum outdoor air flow. When flow is below setpoint for an hour, outdoor air damper should be fully open and return damper closed. When flow is above setpoint for an hour, the opposite should occur.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with economizers
- Climate Zone(s): any
- Component(s): outdoor air dampers, return air dampers, airflow sensors

### Verification Algorithm Pseudo Code

```python
if economizer_lockout(outdoor_air_temp, economizer_high_limit_sp) and sys_mode == 'occupied':
    if outdoor_air_flow < MinOAsp (continuously for 1 hour):
        if outdoor_damper_command == 100 and return_damper_command == 0:
            pass
        else:
            fail
    elif outdoor_air_flow > MinOAsp (continuously for 1 hour):
        if outdoor_damper_command == 0 and return_damper_command == 100:
            pass
        else:
            fail
    else:
        pass  # not enough continuous time above/below setpoint
else:
    untested
```

### Data requirements

- outdoor_air_temp: Outdoor air temperature
  - Data Value Unit: °C
  - Data point Description: Current outdoor air temperature
  - Data Point Affiliation: Environmental conditions

- economizer_high_limit_sp: Economizer high limit
  - Data Value Unit: °C
  - Data point Description: Temperature above which economizer is locked out
  - Data Point Affiliation: Economizer control

- outdoor_damper_command: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current position command to outdoor air damper
  - Data Point Affiliation: Air handling unit

- return_damper_command: Return air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Current position command to return air damper
  - Data Point Affiliation: Air handling unit

- outdoor_air_flow: Outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current outdoor air flow rate
  - Data Point Affiliation: Air handling unit

- min_oa_sp: Minimum outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum outdoor air flow rate setpoint
  - Data Point Affiliation: Air handling unit

- sys_mode: System mode
  - Data Value Unit: enumeration
  - Data point Description: Current AHU operation mode
  - Data Point Affiliation: System control

"""

from constrain.checklib import RuleCheckBase


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
                return "Untested"
        else:
            return "Untested"

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
