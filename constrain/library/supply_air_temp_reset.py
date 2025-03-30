"""
### Description

Section 6.5.3.5 Supply Air Temperature Reset Controls
- Multiple zone HVAC systems must include controls that automatically reset the supply air temperature in response to representative building loads, or to outdoor air temperature. The
controls shall reset the supply air temperature at least 25% of the difference between the design supply air temperature and the design room air temperature. Controls that adjust the
reset based on zone humidity are allowed. Zones that are expected to experience relatively constant loads, such as electronic equipment rooms, shall be designed for the fully reset supply temperature.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.3.5 Supply Air Temperature Reset Controls

### Verification Approach

The verification analyzes supply air temperature setpoint variation:
1. Calculate total reset range (max - min setpoint)
2. Calculate minimum required range:
   - 25% of difference between zone cooling setpoint and minimum SAT
   - Allow 1% tolerance in calculation
3. Pass if actual range meets or exceeds required range
4. Generate distribution plot to visualize setpoint variation

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): air handling units with supply air temperature control
- Climate Zone(s): any
- Component(s): supply air temperature sensors, zone temperature sensors

### Verification Algorithm Pseudo Code

```python
sat_range = max(temperature_air_supply_setpoint) - min(temperature_air_supply_setpoint)
min_sat = min(temperature_air_supply_setpoint)
required_range = (temperature_air_zone_design_cool_setpoint - min_sat) * 0.25 * 0.99

if sat_range >= required_range:
    pass  # Adequate reset range
else:
    fail  # Insufficient reset range
```

### Data requirements

- temperature_air_supply_setpoint: Supply air temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: System control

- temperature_air_zone_design_cool_setpoint: Design zone cooling temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: Zone control

"""

from datetime import date

import matplotlib.pyplot as plt
import seaborn as sns
from constrain.checklib import RuleCheckBase


class SupplyAirTempReset(RuleCheckBase):
    points = [
        "temperature_air_supply_setpoint",
        "temperature_air_zone_design_cool_setpoint",
    ]

    def verify(self):
        t_sa_set_max = max(self.df["temperature_air_supply_setpoint"])
        t_sa_set_min = min(self.df["temperature_air_supply_setpoint"])

        self.result = (t_sa_set_max - t_sa_set_min) >= (
            self.df["temperature_air_zone_design_cool_setpoint"] - t_sa_set_min
        ) * 0.25 * (100 - self.get_tolerance("ratio", "temperature") * 100)

    def plot(self, plot_option, fig_size=(6.4, 4.8), plt_pts=None):
        print(
            "Specific plot method implemented, additional distribution plot is being added!"
        )
        sns.histplot(self.df["temperature_air_supply_setpoint"])
        plt.title("All samples distribution of temperature_air_supply")
        plt.savefig(
            f"{self.results_folder}/All_samples_distribution_of_temperature_air_supply.png"
        )

        super().plot(plot_option, plt_pts, fig_size)

    def calculate_plot_day(self):
        """overwrite method to select day for day plot"""
        for one_day in self.daterange(date(2000, 1, 1), date(2001, 1, 1)):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df.loc[daystr]
            day = self.result[daystr]
            if (
                daydf["temperature_air_supply_setpoint"].max()
                - daydf["temperature_air_supply_setpoint"].min()
                > 0
            ):
                return day, daydf

            return day, daydf
