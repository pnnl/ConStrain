"""
### Description

Section 6.4.3.3.5.2 Guest Room Ventilation Control
Within 30 minutes of all occupants leaving the guest room, ventilation and exhaust fans shall automatically be turned off, or isolation devices serving each guest room shall automatically 
shut off the supply of outdoor air to the guest room and shut off exhaust air from the guest room.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3.3.5.2 Guest Room Ventilation Control

### Verification Approach

The verification checks two scenarios:
1. For unrented rooms (daily occupancy ≈ 0):
   - Ventilation should be completely shut off (zero flow)
2. For rented rooms:
   - Ventilation must be provided continuously
   - Flow rate should match either:
     - Area-based minimum outdoor air requirement, or
     - Air changes based on zone volume

### Verification Applicability

- Building Type(s): hotels, motels
- Space Type(s): guest rooms
- System(s): room HVAC units with ventilation capability
- Climate Zone(s): any
- Component(s): ventilation systems, outdoor air dampers, occupancy sensors

### Verification Algorithm Pseudo Code

```python
for each day:
    if room_not_rented (schedule_occupancy ≈ 0 all day):
        if flow_volumetric_air_outdoor == 0:
            pass  # Proper ventilation shutoff
        else:
            fail  # Ventilation not shut off
    else:  # room is rented
        if flow_volumetric_air_outdoor > 0:
            if flow_volumetric_air_outdoor == flow_volumetric_air_outdoor_per_area * area_zone or
               daily_total_flow == area_zone * height_zone:
                pass  # Proper ventilation provided
            else:
                fail  # Incorrect ventilation rate
        else:
            fail  # No ventilation provided
```

### Data requirements

- flow_volumetric_air_outdoor: Outdoor air flow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone ventilation

- schedule_occupancy: Occupancy schedule
  - Data Value Unit: fraction (0-1)
  - Data Point Affiliation: Zone occupancy

- area_zone: Zone area
  - Data Value Unit: area
  - Data Point Affiliation: Zone configuration

- height_zone: Zone height
  - Data Value Unit: length
  - Data Point Affiliation: Zone configuration

- flow_volumetric_air_outdoor_per_area: Outdoor air requirement
  - Data Value Unit: volumetric flow rate per area
  - Data Point Affiliation: Zone ventilation

"""

import pandas as pd
from constrain.checklib import CheckLibBase


class GuestRoomControlVent(CheckLibBase):
    points = [
        "flow_volumetric_air_outdoor",
        "schedule_occupancy",
        "area_zone",
        "height_zone",
        "flow_volumetric_air_outdoor_per_area",
    ]

    def verify(self):
        zone_volume = self.df["area_zone"][0] * self.df["height_zone"][0]
        m_z_oa_set = (
            self.df["flow_volumetric_air_outdoor_per_area"][0] * self.df["area_zone"][0]
        )

        year_info = 2000
        result_repo = []
        for idx, day in self.df.groupby(self.df.index.date):
            if day.index.month[0] == 2 and day.index.day[0] == 29:
                pass
            elif year_info != day.index.year[0]:
                pass
            else:
                if (
                    day["schedule_occupancy"]
                    <= self.get_tolerance("ratio", "occupancy")
                ).all():  # confirmed this room is NOT rented out
                    if (
                        abs(day["flow_volumetric_air_outdoor"])
                        < self.get_tolerance("airflow", "outdoor_air")
                    ).all():
                        result_repo.append(1)  # pass,
                    else:
                        result_repo.append(0)  # fail
                else:  # room is rented out
                    if (
                        day["flow_volumetric_air_outdoor"]
                        > self.get_tolerance("airflow", "outdoor_air")
                    ).all():
                        if abs(
                            day["flow_volumetric_air_outdoor"] - m_z_oa_set
                        ) < self.get_tolerance("airflow", "outdoor_air") or abs(
                            day["flow_volumetric_air_outdoor"].sum(axis=1) - zone_volume
                        ) < self.get_tolerance(
                            "airflow", "outdoor_air"
                        ):
                            result_repo.append(1)  # pass
                        else:
                            result_repo.append(0)  # fail
                    else:
                        result_repo.append(0)
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
