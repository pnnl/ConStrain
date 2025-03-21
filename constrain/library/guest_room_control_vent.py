"""
### Description

This verification aims to check if guest room ventilation rates are properly controlled based on occupancy status. The system should automatically turn off ventilation during unrented periods and provide appropriate ventilation when rooms are rented.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.4.3.3.5 Automatic Control of HVAC in Hotel/Motel Guest Rooms
- Code Subsection: Ventilation Control

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
    if room_not_rented (occupancy ≈ 0 all day):
        if outdoor_air_flow == 0:
            pass  # Proper ventilation shutoff
        else:
            fail  # Ventilation not shut off
    else:  # room is rented
        if outdoor_air_flow > 0:
            if outdoor_air_flow == area_based_minimum or
               daily_total_flow == zone_volume:
                pass  # Proper ventilation provided
            else:
                fail  # Incorrect ventilation rate
        else:
            fail  # No ventilation provided
```

### Data requirements

- m_z_oa: Outdoor air flow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Zone outdoor air ventilation rate
  - Data Point Affiliation: Room ventilation control

- O_sch: Occupancy schedule
  - Data Value Unit: fraction (0-1)
  - Data point Description: Room occupancy status
  - Data Point Affiliation: Room monitoring

- area_z: Zone area
  - Data Value Unit: square meters
  - Data point Description: Floor area of the guest room
  - Data Point Affiliation: Room configuration

- height_z: Zone height
  - Data Value Unit: meters
  - Data point Description: Floor-to-ceiling height of the guest room
  - Data Point Affiliation: Room configuration

- v_outdoor_per_zone: Outdoor air requirement
  - Data Value Unit: volumetric flow rate per area
  - Data point Description: Required outdoor air flow rate per unit area
  - Data Point Affiliation: System configuration

- tol_occ: Occupancy tolerance
  - Data Value Unit: fraction
  - Data point Description: Threshold for considering room unoccupied
  - Data Point Affiliation: System configuration

- tol_oa_flow: Flow tolerance
  - Data Value Unit: volumetric flow rate
  - Data point Description: Allowable deviation from required flow rates
  - Data Point Affiliation: System configuration

"""

import pandas as pd
from constrain.checklib import CheckLibBase


class GuestRoomControlVent(CheckLibBase):
    points = [
        "m_z_oa",
        "O_sch",
        "area_z",
        "height_z",
        "v_outdoor_per_zone",
        "tol_occ",
        "tol_oa_flow",
    ]

    def verify(self):
        tol_occ = self.df["tol_occ"][0]
        tol_m = self.df["tol_oa_flow"][0]
        zone_volume = self.df["area_z"][0] * self.df["height_z"][0]
        m_z_oa_set = self.df["v_outdoor_per_zone"][0] * self.df["area_z"][0]

        year_info = 2000
        result_repo = []
        for idx, day in self.df.groupby(self.df.index.date):
            if day.index.month[0] == 2 and day.index.day[0] == 29:
                pass
            elif year_info != day.index.year[0]:
                pass
            else:
                if (
                    day["O_sch"] <= tol_occ
                ).all():  # confirmed this room is NOT rented out
                    if (day["m_z_oa"] == 0).all():
                        result_repo.append(1)  # pass,
                    else:
                        result_repo.append(0)  # fail
                else:  # room is rented out
                    if (day["m_z_oa"] > 0).all():
                        if (
                            day["m_z_oa"] == m_z_oa_set
                            or day["m_z_oa"].sum(axis=1) == zone_volume
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
