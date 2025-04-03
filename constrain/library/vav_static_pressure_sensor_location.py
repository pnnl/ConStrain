"""
### Description

Section 6.5.3.2.2 VAV Static Pressure Sensor Location
- Static pressure sensors used to control VAV fans shall be located such that the controller set point is no greater than 1.2 in. of water. If this results in the sensor being located downstream
of major duct splits, sensors shall be installed in each major branch to ensure that static pressure can be maintained in each.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.3.2.2 VAV Static Pressure Sensor Location

### Verification Approach

The verification monitors duct static pressure setpoint:
1. Compare setpoint to maximum allowed pressure:
   - Maximum = 1.2 inches w.g. (298.608 Pa)
   - Allow small tolerance in measurement
2. Pass if setpoint stays below limit
3. Generate daily plots to visualize pressure control

### Verification Applicability

- Building Type(s): any with VAV systems
- Space Type(s): any
- System(s): VAV air handling units
- Climate Zone(s): any
- Component(s): static pressure sensors, duct systems

### Verification Algorithm Pseudo Code

```python
max_pressure = 298.608  # Pa (1.2 inches w.g.)

if pressure_static_setpoint < max_pressure:
    pass  # Proper sensor location/control
else:
    fail  # Excessive duct pressure
```

### Data requirements

- pressure_static_setpoint: Pressure setpoint
  - Data Value Unit: pressure
  - Data Point Affiliation: System control

"""

from datetime import date

from constrain.checklib import RuleCheckBase


class VAVStaticPressureSensorLocation(RuleCheckBase):
    points = ["pressure_static_setpoint"]

    def verify(self):
        self.result = self.df["pressure_static_setpoint"] < (
            298.608 + self.get_tolerance("pressure", "static")
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
