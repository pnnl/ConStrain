"""
### Description

section 6.4.3.4.4 Ventilation Fan Controls
- Fans with motors greater than 0.75 hp shall have automatic controls complying with Section 6.4.3.3.1 that are capable of and configured to shut off fans when not required.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3.4.4 Ventilation Fan Controls

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
if heat_sensible == 0 and number_occupants == 0 and power_fan != 0:
    fail
else:
    pass
```

### Data requirements

- heat_sensible: Zone sensible heat load
  - Data Value Unit: power
  - Data Point Affiliation: Zone monitoring

- number_occupants: Occupancy count
  - Data Value Unit: count
  - Data Point Affiliation: Zone monitoring

- power_fan: Fan power
  - Data Value Unit: power
  - Data Point Affiliation: Equipment monitoring

"""

from datetime import date

from constrain.checklib import RuleCheckBase


class VentilationFanControl(RuleCheckBase):
    points = ["heat_sensible", "number_occupants", "power_fan"]

    def verify(self):
        self.result = ~(
            (abs(self.df["heat_sensible"]) < self.get_tolerance("load", "zone"))
            & (self.df["number_occupants"] == 0)
            & (abs(self.df["power_fan"]) > self.get_tolerance("power", "fan"))
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
