"""
### Description

This verification aims to check if ventilation fans are properly controlled based on space occupancy and load conditions. The system should shut off ventilation fans when spaces are unoccupied and have no load requirements.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.4.3.3 Ventilation Controls for High-Occupancy Areas
- Code Subsection: Ventilation Fan Control Requirements

### Verification Approach

The verification monitors three key conditions:
1. Space load status:
   - Check if there is any heating/cooling load
2. Occupancy status:
   - Check if any occupants are present
3. Fan operation:
   - Verify fan is off when both load and occupancy are zero
   - Generate daily plots to visualize control behavior

### Verification Applicability

- Building Type(s): any
- Space Type(s): any with variable occupancy
- System(s): ventilation systems
- Climate Zone(s): any
- Component(s): ventilation fans, occupancy sensors

### Verification Algorithm Pseudo Code

```python
if space_load == 0 and occupancy == 0:
    if fan_power != 0:
        fail  # Fan running unnecessarily
    else:
        pass  # Proper fan control
else:
    pass  # Fan operation may be needed
```

### Data requirements

- Q_load: Space load
  - Data Value Unit: watts
  - Data point Description: Current space heating/cooling load
  - Data Point Affiliation: Space monitoring

- no_of_occ: Occupancy count
  - Data Value Unit: count
  - Data point Description: Number of occupants in space
  - Data Point Affiliation: Space monitoring

- P_fan: Fan power
  - Data Value Unit: watts
  - Data point Description: Ventilation fan power consumption
  - Data Point Affiliation: Equipment monitoring

"""

from datetime import date

from constrain.checklib import RuleCheckBase


class VentilationFanControl(RuleCheckBase):
    points = ["Q_load", "no_of_occ", "P_fan"]

    def verify(self):
        self.result = ~(
            (self.df["Q_load"] == 0)
            & (self.df["no_of_occ"] == 0)
            & (self.df["P_fan"] != 0)
        )

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(
            date(self.df.index[0].year, self.df.index[0].month, self.df.index[0].day),
            date(
                self.df.index[-1].year, self.df.index[-1].month, self.df.index[-1].day
            ),
        ):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df.loc[daystr]
            day = self.result[daystr]

            return day, daydf
