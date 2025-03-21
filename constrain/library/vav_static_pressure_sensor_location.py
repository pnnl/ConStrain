"""
### Description

This verification aims to check if static pressure sensors in VAV systems are properly located to prevent excessive duct pressure. The system should maintain duct static pressure below 1.2 inches water gauge (298.608 Pa) to minimize energy use and avoid duct leakage.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.5.3.2 Fan Control
- Code Subsection: Static Pressure Sensor Location

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

if pressure_setpoint < max_pressure + tolerance:
    pass  # Proper sensor location/control
else:
    fail  # Excessive duct pressure
```

### Data requirements

- p_fan_set: Pressure setpoint
  - Data Value Unit: pascals
  - Data point Description: Duct static pressure setpoint
  - Data Point Affiliation: System control

- tol_P_fan: Pressure tolerance
  - Data Value Unit: pascals
  - Data point Description: Allowable deviation from pressure limit
  - Data Point Affiliation: System configuration

"""

from datetime import date

from constrain.checklib import RuleCheckBase


class VAVStaticPressureSensorLocation(RuleCheckBase):
    points = ["p_fan_set", "tol_P_fan"]

    def verify(self):
        self.result = self.df["p_fan_set"] < 298.608 + self.df["tol_P_fan"]

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
