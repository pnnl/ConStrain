"""
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
if economizer_lockout(temperature_air_outdoor, temperature_air_economizer_limit) and mode_system == 'occupied':
    if flow_volumetric_air_outdoor < flow_volumetric_air_outdoor_setpoint_min (continuously for 1 hour):
        if position_damper_air_outdoor == 100 and position_damper_air_return == 0:
            pass
        else:
            fail
    elif flow_volumetric_air_outdoor > flow_volumetric_air_outdoor_setpoint_min (continuously for 1 hour):
        if position_damper_air_outdoor == 0 and position_damper_air_return == 100:
            pass
        else:
            fail
    else:
        pass  # not enough continuous time above/below setpoint
else:
    untested
```

### Data requirements

- temperature_air_outdoor: Outdoor air temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Environmental conditions

- temperature_air_economizer_limit: Economizer high limit temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Economizer control

- position_damper_air_outdoor: Outdoor air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- position_damper_air_return: Return air damper position
  - Data Value Unit: percent
  - Data Point Affiliation: Air handling unit

- flow_volumetric_air_outdoor: Outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Air handling unit

- flow_volumetric_air_outdoor_setpoint_min: Minimum outdoor airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Air handling unit

- mode_system: System mode (If mode_system is not "occupied", this verification item results fall into ""Untested)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

"""

from constrain.checklib import RuleCheckBase


class G36MinOAwoEconomizer(RuleCheckBase):
    points = [
        "temperature_air_outdoor",
        "temperature_air_economizer_limit",
        "position_damper_air_outdoor",
        "position_damper_air_return",
        "flow_volumetric_air_outdoor",
        "flow_volumetric_air_outdoor_setpoint_min",
        "mode_system",
    ]

    def economizer_lockout(
        self, temperature_air_outdoor, temperature_air_economizer_limit
    ):
        if temperature_air_outdoor > temperature_air_economizer_limit:
            return True
        else:
            return False

    def ts_verify_logic(self, t):
        if (
            self.economizer_lockout(
                t["temperature_air_outdoor"], t["temperature_air_economizer_limit"]
            )
            and t["mode_system"].strip().lower() == "occupied"
        ):
            if t["oaf_low_timer"] > 60:
                if (
                    t["position_damper_air_outdoor"]
                    > (100 - self.get_tolerance("damper", "command") * 100)
                    and t["position_damper_air_return"] < 100
                ):
                    return True
                else:
                    return False
            elif t["oaf_high_timer"] > 60:
                if t["position_damper_air_outdoor"] < 100 and t[
                    "position_damper_air_return"
                ] > (100 - self.get_tolerance("damper", "command") * 100):
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
                    t["temperature_air_outdoor"], t["temperature_air_economizer_limit"]
                )
                and t["mode_system"].strip().lower() == "occupied"
            ):
                # only count the timers when it is in occupied mode with economizer lockout
                if t["flow_volumetric_air_outdoor"] < t[
                    "flow_volumetric_air_outdoor_setpoint_min"
                ] - self.get_tolerance("airflow", "outdoor_air"):
                    high_timer_start = None
                    high_timer_list.append(0)
                    if low_timer_start is None:
                        low_timer_start = i
                        low_timer_list.append(0)
                    else:
                        low_timer_list.append(
                            (i - low_timer_start).total_seconds() / 60
                        )
                if t["flow_volumetric_air_outdoor"] > t[
                    "flow_volumetric_air_outdoor_setpoint_min"
                ] + self.get_tolerance("airflow", "outdoor_air"):
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
