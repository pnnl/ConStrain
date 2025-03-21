"""
### Description

This verification aims to check if the hot water temperature reset control operates correctly based on outdoor air temperature. The system should adjust hot water temperature setpoints to optimize energy efficiency while maintaining comfort.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.5.4.4 Hydronic System Controls
- Code Subsection: Hot Water Temperature Reset

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

- T_oa_db: Outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Current outdoor air dry-bulb temperature
  - Data Point Affiliation: Environmental conditions

- T_oa_max: Maximum outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Upper threshold for temperature reset
  - Data Point Affiliation: System configuration

- T_oa_min: Minimum outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Lower threshold for temperature reset
  - Data Point Affiliation: System configuration

- T_hw: Hot water temperature
  - Data Value Unit: °C
  - Data point Description: Current hot water supply temperature
  - Data Point Affiliation: System monitoring

- m_hw: Hot water flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current hot water flow rate
  - Data Point Affiliation: System monitoring

- T_hw_max_sp: Maximum temperature setpoint
  - Data Value Unit: °C
  - Data point Description: Maximum hot water temperature setpoint
  - Data Point Affiliation: System control

- T_hw_min_sp: Minimum temperature setpoint
  - Data Value Unit: °C
  - Data point Description: Minimum hot water temperature setpoint
  - Data Point Affiliation: System control

"""

import matplotlib.pyplot as plt
import seaborn as sns
from constrain.checklib import RuleCheckBase


class HWReset(RuleCheckBase):
    points = [
        "T_oa_db",
        "T_oa_max",
        "T_oa_min",
        "T_hw",
        "m_hw",
        "T_hw_max_sp",
        "T_hw_min_sp",
    ]

    def verify(self):
        self.result = (
            (
                self.df["m_hw"] <= 0
            )  # add boundary relaxation in the rules for this one and chwreset
            | (
                (self.df["T_oa_db"] <= self.df["T_oa_min"])
                & (self.df["T_hw"] >= self.df["T_hw_max_sp"] * 0.99)
            )
            | (
                (self.df["T_oa_db"] >= (self.df["T_oa_max"]))
                & (self.df["T_hw"] <= self.df["T_hw_min_sp"] * 1.01)
            )
            | (
                (
                    (self.df["T_oa_db"] >= self.df["T_oa_min"])
                    & (self.df["T_oa_db"] <= self.df["T_oa_max"])
                )
                & (
                    (self.df["T_hw"] >= self.df["T_hw_min_sp"] * 0.99)
                    & (self.df["T_hw"] <= self.df["T_hw_max_sp"] * 1.01)
                )
            )
        )

    # Add a correlation scatter plot of T_oa_db and T_hw
    def plot(self, plot_option, fig_size, plt_pts=None):
        print(
            "Specific plot method implemented, additional scatter plot is being added!"
        )
        plt.subplots()
        sns.scatterplot(x="T_oa_db", y="T_hw", data=self.df)
        plt.title("Scatter plot between T_oa_db and T_hw")

        super().plot(plot_option, plt_pts)
