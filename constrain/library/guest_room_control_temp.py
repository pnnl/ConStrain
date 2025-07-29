"""
### Description

Section 6.4.3.3.5.1 Guest Room HVAC Set-Point Control
- Within 30 minutes of all occupants leaving the guest room, HVAC set points shall be automatically raised by at least 4°F from the occupant set point in the cooling mode and automatically
lowered by at least 4°F from the occupant set point in the heating mode. When the guest room is unrented and unoccupied, HVAC set points shall be automatically reset to 80°F or higher in the cooling mode and to 60°F or lower in the heating mode.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3.3.5.1 Guest Room HVAC Set-Point Control

### Verification Approach

The verification checks two scenarios:
1. For unrented rooms (daily occupancy ≈ 0):
   - Heating setpoint should be below 15.6°C (60°F)
   - Cooling setpoint should be above 26.7°C (80°F)
2. For rented rooms with temporary vacancy:
   - Heating setpoint should decrease by at least 2.22°C (4°F)
   - Cooling setpoint should increase by at least 2.22°C (4°F)

### Verification Applicability

- Building Type(s): hotels, motels
- Space Type(s): guest rooms
- System(s): room HVAC units
- Climate Zone(s): any
- Component(s): thermostats, occupancy sensors

### Verification Algorithm Pseudo Code

```python
for each day:
    if room_not_rented (occupancy ≈ 0 all day):
        if temperature_air_zone_heat_setpoint < 15.6°C and temperature_air_zone_cool_setpoint > 26.7°C:
            pass  # Proper setback for unrented room
        else:
            fail  # Setback not implemented
    else:  # room is rented
        occupied_heating_sp = max(temperature_air_zone_heat_setpoint during occupied periods)
        occupied_cooling_sp = min(temperature_air_zone_cool_setpoint during occupied periods)
        
        if temperature_air_zone_heat_setpoint < (occupied_heating_sp - 2.22°C) or
           temperature_air_zone_cool_setpoint > (occupied_cooling_sp + 2.22°C):
            pass  # Proper setback when guests leave
        else:
            fail  # Insufficient setback
```

### Data requirements

- temperature_air_zone_heat_setpoint: Heating setpoint
  - Data Value Unit: °C
  - Data Point Affiliation: Zone temperature control

- temperature_air_zone_cool_setpoint: Cooling setpoint
  - Data Value Unit: °C
  - Data Point Affiliation: Zone temperature control

- schedule_occupancy: Occupancy schedule
  - Data Value Unit: fraction (0-1)
  - Data Point Affiliation: Zone occupancy

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class GuestRoomControlTemp(RuleCheckBase):
    points = [
        "temperature_air_zone_heat_setpoint",
        "temperature_air_zone_cool_setpoint",
        "schedule_occupancy",
    ]

    def verify(self):
        year_info = 2000
        result_repo = []
        for idx, day in self.df.groupby(self.df.index.date):
            if (
                day.index.month[0] == 2 and day.index.day[0] == 29
            ):  # skip leap year, although E+ doesn't have leap year the date for loop assumes so because 24:00 time step so, it's intentionally skipped here
                pass
            elif (
                year_info != day.index.year[0]
            ):  # remove the Jan 1st of next year reason: the pandas date for loop iterates one more loop is hour is 24:00:00
                pass
            else:
                if (
                    day["schedule_occupancy"]
                    <= self.get_tolerance("ratio", "occupancy")
                ).all():  # confirmed this room is NOT rented out
                    if (
                        day["temperature_air_zone_heat_setpoint"]
                        < 15.6 + self.get_tolerance("temperature", "zone")
                    ).all() and (
                        day["temperature_air_zone_cool_setpoint"]
                        > 26.7 - self.get_tolerance("temperature", "zone")
                    ).all():
                        result_repo.append(
                            1
                        )  # pass, confirmed zone temperature setpoint reset during the unrented period
                    else:
                        result_repo.append(
                            0
                        )  # fail, zone temperature setpoint was not reset correctly
                else:  # room is rented out
                    T_z_hea_occ_set = day.query("schedule_occupancy > 0.0")[
                        "temperature_air_zone_heat_setpoint"
                    ].max()
                    T_z_coo_occ_set = day.query("schedule_occupancy > 0.0")[
                        "temperature_air_zone_cool_setpoint"
                    ].min()

                    if (
                        day["temperature_air_zone_heat_setpoint"]
                        < T_z_hea_occ_set
                        - 2.22
                        + self.get_tolerance("temperature", "zone")
                    ).all() or (
                        day["temperature_air_zone_cool_setpoint"]
                        > T_z_coo_occ_set
                        + 2.22
                        - self.get_tolerance("temperature", "zone")
                    ).all():
                        result_repo.append(
                            1
                        )  # pass, confirm the HVAC setpoint control resets when guest room reset when occupants leave the room
                    else:
                        result_repo.append(
                            0
                        )  # fail, reset does not meet the standard or no reset was observed.
                year_info = day.index.year[0]

        dti = pd.date_range("2020-01-01", periods=365, freq="D")
        self.result = pd.Series(result_repo, index=dti)

    def check_bool(self) -> bool:
        if len(self.result[self.result == 1] > 0):
            return True
        else:
            return False

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == 1]),
            "Fail #": len(self.result[self.result == 0]),
            "Verification Passed?": self.check_bool(),
        }
        print(output)
        return output

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
