"""
### Description

6.5.4.4 Chilled- and Hot-Water Temperature Reset Controls
- Chilled- and hot-water systems with a design capacity exceeding 300,000 Btu/h supplying chilled or heated water to comfort conditioning systems shall include controls that automatically
reset supply water temperatures by representative building loads (including return water temperature) or by outdoor air temperature. Where DDC is used to control valves, the
set point shall be reset based on valve positions until one valve is nearly wide open or setpoint limits of the system equipment or application have been reached.

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
if flow_mass_water_hot <= 0:
    pass  # No flow condition
elif temperature_air_outdoor <= temperature_air_outdoor_min:
    if temperature_water_hot >= temperature_water_hot_setpoint_max * 0.99:
        pass  # Proper reset at low outdoor temp
    else:
        fail
elif temperature_air_outdoor >= temperature_air_outdoor_max:
    if temperature_water_hot <= temperature_water_hot_setpoint_min * 1.01:
        pass  # Proper reset at high outdoor temp
    else:
        fail
elif temperature_air_outdoor_min < temperature_air_outdoor < temperature_air_outdoor_max:
    if temperature_water_hot_setpoint_min * 0.99 <= temperature_water_hot <= temperature_water_hot_setpoint_max * 1.01:
        pass  # Proper reset during intermediate conditions
    else:
        fail
```

### Data requirements

- temperature_air_outdoor: Outdoor temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Environmental conditions

- temperature_air_outdoor_max: Maximum outdoor temperature
  - Data Value Unit: °C
  - Data Point Affiliation: System configuration

- temperature_air_outdoor_min: Minimum outdoor temperature
  - Data Value Unit: °C
  - Data Point Affiliation: System configuration

- temperature_water_hot: Hot water temperature
  - Data Value Unit: °C
  - Data Point Affiliation: System monitoring

- flow_mass_water_hot: Hot water flow
  - Data Value Unit: mass flow rate
  - Data Point Affiliation: System monitoring

- temperature_water_hot_setpoint_max: Maximum temperature setpoint
  - Data Value Unit: °C
  - Data Point Affiliation: System control

- temperature_water_hot_setpoint_min: Minimum temperature setpoint
  - Data Value Unit: °C
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
            (self.df["flow_mass_water_hot"] <= self.get_tolerance("waterflow", "hot"))
            | (
                (
                    self.df["temperature_air_outdoor"]
                    <= self.df["temperature_air_outdoor_min"]
                    + self.get_tolerance("temperature", "outdoor_air")
                )
                & (
                    self.df["temperature_water_hot"]
                    >= self.df["temperature_water_hot_setpoint_max"]
                    - self.get_tolerance("temperature", "general")
                )
            )
            | (
                (
                    self.df["temperature_air_outdoor"]
                    >= (
                        self.df["temperature_air_outdoor_max"]
                        - self.get_tolerance("temperature", "outdoor_air")
                    )
                )
                & (
                    self.df["temperature_water_hot"]
                    <= self.df["temperature_water_hot_setpoint_min"]
                    + self.get_tolerance("temperature", "general")
                )
            )
            | (
                (
                    (
                        self.df["temperature_air_outdoor"]
                        >= self.df["temperature_air_outdoor_min"]
                        - self.get_tolerance("temperature", "outdoor_air")
                    )
                    & (
                        self.df["temperature_air_outdoor"]
                        <= self.df["temperature_air_outdoor_max"]
                        + self.get_tolerance("temperature", "outdoor_air")
                    )
                )
                & (
                    (
                        self.df["temperature_water_hot"]
                        >= self.df["temperature_water_hot_setpoint_min"]
                        + self.get_tolerance("temperature", "general")
                    )
                    & (
                        self.df["temperature_water_hot"]
                        <= self.df["temperature_water_hot_setpoint_max"]
                        - self.get_tolerance("temperature", "general")
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
