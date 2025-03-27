"""
### Description

This verification aims to check if the hot water temperature reset control operates correctly based on outdoor air temperature. The system should adjust hot water temperature setpoints to optimize energy efficiency while maintaining comfort.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.4.4 Chilled- and Hot-Water Temperature Reset Controls

### Verification Approach

The verification checks hot water temperature control under three conditions:
1. When outdoor temperature ≤ minimum threshold:
   - Hot water temperature should be at maximum setpoint
2. When outdoor temperature ≥ maximum threshold:
   - Hot water temperature should be at minimum setpoint
3. When outdoor temperature is between thresholds:
   - Hot water temperature should modulate between min/max setpoints
Note: Verification is bypassed when there is no hot water flow.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): hydronic heating systems
- Climate Zone(s): any
- Component(s): hot water temperature sensors, outdoor air sensors

### Verification Algorithm Pseudo Code

```python
if hot_water_flow <= 0:
    pass  # No flow condition
elif outdoor_temp <= outdoor_min:
    if hot_water_temp >= hot_water_max_sp * 0.99:
        pass  # Proper reset at low outdoor temp
    else:
        fail
elif outdoor_temp >= outdoor_max:
    if hot_water_temp <= hot_water_min_sp * 1.01:
        pass  # Proper reset at high outdoor temp
    else:
        fail
elif outdoor_min < outdoor_temp < outdoor_max:
    if hot_water_min_sp * 0.99 <= hot_water_temp <= hot_water_max_sp * 1.01:
        pass  # Proper reset during intermediate conditions
    else:
        fail
```

### Data requirements

- t_oa: Outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Outdoor air temperature
  - Data Point Affiliation: Environmental conditions

- t_oa_max: Maximum outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Maximum outdoor air temperature
  - Data Point Affiliation: System configuration

- t_oa_min: Minimum outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Minimum outdoor air temperature
  - Data Point Affiliation: System configuration

- t_hw: Hot water temperature
  - Data Value Unit: °C
  - Data point Description: Hot water temperature
  - Data Point Affiliation: System monitoring

- m_hw: Hot water flow
  - Data Value Unit: mass flow rate
  - Data point Description: Hot water mass flow rate
  - Data Point Affiliation: System monitoring

- t_hw_max_sp: Maximum temperature setpoint
  - Data Value Unit: °C
  - Data point Description: Hot water maximum temperature setpoint
  - Data Point Affiliation: System control

- t_hw_min_sp: Minimum temperature setpoint
  - Data Value Unit: °C
  - Data point Description: Hot water minimum temperature setpoint
  - Data Point Affiliation: System control

"""

import matplotlib.pyplot as plt
import seaborn as sns
from constrain.checklib import RuleCheckBase


class HWReset(RuleCheckBase):
    points = [
        "temperature_air_outdoor",
        "temperature_air_outdoor_max",
        "temperature_air_outdoor_min",
        "temperature_water_hot",
        "flow_mass_water_hot",
        "temperature_water_hot_setpoint_max",
        "temperature_water_hot_setpoint_min",
    ]

    def verify(self):
        self.result = (
            (
                self.df["flow_mass_water_hot"] <= 0
            )  # add boundary relaxation in the rules for this one and chwreset
            | (
                (
                    self.df["temperature_air_outdoor"]
                    <= self.df["temperature_air_outdoor_min"]
                )
                & (
                    self.df["temperature_water_hot"]
                    >= self.df["temperature_water_hot_setpoint_max"] * 0.99
                )
            )
            | (
                (
                    self.df["temperature_air_outdoor"]
                    >= (self.df["temperature_air_outdoor_max"])
                )
                & (
                    self.df["temperature_water_hot"]
                    <= self.df["temperature_water_hot_setpoint_min"] * 1.01
                )
            )
            | (
                (
                    (
                        self.df["temperature_air_outdoor"]
                        >= self.df["temperature_air_outdoor_min"]
                    )
                    & (
                        self.df["temperature_air_outdoor"]
                        <= self.df["temperature_air_outdoor_max"]
                    )
                )
                & (
                    (
                        self.df["temperature_water_hot"]
                        >= self.df["temperature_water_hot_setpoint_min"] * 0.99
                    )
                    & (
                        self.df["temperature_water_hot"]
                        <= self.df["temperature_water_hot_setpoint_max"] * 1.01
                    )
                )
            )
        )

    # Add a correlation scatter plot of t_oa and t_hw
    def plot(self, plot_option, fig_size, plt_pts=None):
        print(
            "Specific plot method implemented, additional scatter plot is being added!"
        )
        plt.subplots()
        sns.scatterplot(
            x="temperature_air_outdoor", y="temperature_water_hot", data=self.df
        )
        plt.title("Scatter plot between t_oa and t_hw")

        super().plot(plot_option, plt_pts)
