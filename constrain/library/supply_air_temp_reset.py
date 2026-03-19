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
import numpy as np
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
        ) * 0.25 * (1 - self.get_tolerance("ratio", "temperature") * 1)

    def fd_bins(self, data, min_bins=5, max_bins=100):
        data = np.asarray(data)
        data = data[~np.isnan(data)]
        if data.size < 2:
            return 1

        q25, q75 = np.percentile(data, [25, 75])
        iqr = q75 - q25
        if iqr == 0:
            # fall back to std or Sturges
            std = data.std(ddof=1)
            if std == 0:
                return 1
            bin_width = 3.5 * std / (data.size ** (1 / 3))
        else:
            bin_width = 2 * iqr / (data.size ** (1 / 3))

        data_range = data.max() - data.min()
        if bin_width <= 0 or data_range == 0:
            return 1

        n_bins = int(np.ceil(data_range / bin_width))
        n_bins = max(min_bins, n_bins)
        n_bins = min(max_bins, n_bins)
        return n_bins

    def plot(self, plot_option, fig_size=(6.4, 4.8), plt_pts=None):
        print(
            "Specific plot method implemented, additional distribution plot is being added!"
        )
        sns.histplot(
            self.df["temperature_air_supply_setpoint"],
            bins=self.fd_bins(self.df["temperature_air_supply_setpoint"]),
            stat="count",
        )
        plt.title("Distribution of Supply Air Temperature Setpoint")
        plt.xlabel("Temperature")
        plt.ylabel("Count")
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
