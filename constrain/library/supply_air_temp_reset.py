"""
### Description

This verification aims to check if the supply air temperature reset strategy provides adequate range of adjustment. The system should reset supply air temperature based on building loads to improve energy efficiency while maintaining comfort.

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
sat_range = max(t_sa_sp) - min(t_sa_sp)
min_sat = min(t_sa_sp)
required_range = (t_z_design_cool - min_sat) * 0.25 * 0.99

if sat_range >= required_range:
    pass  # Adequate reset range
else:
    fail  # Insufficient reset range
```

### Data requirements

- t_sa_sp: Supply air temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Supply air temperature setpoint
  - Data Point Affiliation: System control

- t_z_design_cool: Design zone cooling temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Design zone cooling temperature setpoint
  - Data Point Affiliation: Zone control

"""

from datetime import date

import matplotlib.pyplot as plt
import seaborn as sns
from constrain.checklib import RuleCheckBase


class SupplyAirTempReset(RuleCheckBase):
    points = ["temperature_air_supply", "temperature_air_zone_design_cool_setpoint"]

    def verify(self):
        t_sa_sp_max = max(self.df["temperature_air_supply"])
        t_sa_sp_min = min(self.df["temperature_air_supply"])

        self.result = (t_sa_sp_max - t_sa_sp_min) >= (
            self.df["temperature_air_zone_design_cool_setpoint"] - t_sa_sp_min
        ) * 0.25 * 0.99  # 0.99 being the numeric threshold

    def plot(self, plot_option, fig_size=(6.4, 4.8), plt_pts=None):
        print(
            "Specific plot method implemented, additional distribution plot is being added!"
        )
        sns.histplot(self.df["temperature_air_supply"])
        plt.title("All samples distribution of t_sa_sp")
        plt.savefig(f"{self.results_folder}/All_samples_distribution_of_t_sa_sp.png")

        super().plot(plot_option, plt_pts, fig_size)

    def calculate_plot_day(self):
        """over write method to select day for day plot"""
        for one_day in self.daterange(date(2000, 1, 1), date(2001, 1, 1)):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df.loc[daystr]
            day = self.result[daystr]
            if (
                daydf["temperature_air_supply"].max()
                - daydf["temperature_air_supply"].min()
                > 0
            ):
                return day, daydf
            return day, daydf
