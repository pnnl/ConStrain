"""
### Description

Section 6.5.5.2.1
The fan system on a heat-rejection device powered by an individual motor or an array of motors with a connected power, including the motor service factor, totaling 5 hp or more 
shall have controls and/or devices (such as variable-speed control) that shall result in fan motor demand of no more than 30% of design wattage at 50% of the design airflow and that 
shall automatically modulate the fan speed to control the leaving fluid temperature or condensing temperature/pressure of the heat-rejection device.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.5.2 Fan Speed Control
- Code Subsection: 6.5.5.2.1  

### Verification Approach

The verification analyzes the relationship between normalized fan power and normalized airflow:
1. Filter out zero power points and flows below 50% of design
2. Perform linear regression on transformed data (power-1 vs flow-1)
3. Check if power reduction coefficient is at least 1.4
   - This ensures fan power drops faster than flow rate
   - Approximates cubic relationship between power and flow

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): cooling towers, fluid coolers
- Climate Zone(s): any
- Component(s): heat rejection fans, VFDs

### Verification Algorithm Pseudo Code

```python
# Normalize data
fan_flow = ratio_flow_coolingtower * flow_volumetric_air_coolingtower_design
normalized_flow = fan_flow / flow_volumetric_air_coolingtower_design
normalized_power = power_fan_coolingtower / power_fan_coolingtower_design

# Transform data for analysis
transformed_flow = normalized_flow - 1
transformed_power = normalized_power - 1

# Filter data
valid_points = transformed_flow > -0.5  # flow > 50% of design

# Linear regression
coefficient = linear_regression(transformed_flow, transformed_power)

if coefficient >= 1.4:
    pass  # Power reduction meets requirements
else:
    fail  # Insufficient power reduction at part load
```

### Data requirements

- power_fan_coolingtower: Cooling tower fan power
  - Data Value Unit: power
  - Data Point Affiliation: Fan monitoring

- ratio_flow_coolingtower: Cooling tower flow ratio
  - Data Value Unit: fraction
  - Data Point Affiliation: Fan control

- power_fan_coolingtower_design: Cooling tower design fan power
  - Data Value Unit: power
  - Data Point Affiliation: Equipment specifications

- flow_volumetric_air_coolingtower_design: Cooling tower design volumetric flow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Equipment specifications

"""

from typing import Dict

from constrain.checklib import RuleCheckBase
from sklearn.linear_model import LinearRegression


class HeatRejectionFanVariableFlowControl(RuleCheckBase):
    points = [
        "power_fan_coolingtower",
        "ratio_flow_coolingtower",
        "power_fan_coolingtower_design",
        "flow_volumetric_air_coolingtower_design",
    ]

    def verify(self):
        self.df["v_fan"] = (
            self.df["ratio_flow_coolingtower"]
            * self.df["flow_volumetric_air_coolingtower_design"]
        )
        self.df["normalized_v_fan"] = (
            self.df["v_fan"] / self.df["flow_volumetric_air_coolingtower_design"]
        )
        self.df["normalized_p_power_fan_ct"] = (
            self.df["power_fan_coolingtower"] / self.df["power_fan_coolingtower_design"]
        )

        self.df = self.df.loc[
            self.df["normalized_p_power_fan_ct"] > 0.0
        ]  # filter out 0 values
        self.df["normalized_v_fan"] -= 1  # minus 1 to transform the data
        self.df["normalized_p_power_fan_ct"] -= 1

        self.df = self.df.loc[
            self.df["normalized_v_fan"] > -0.5
        ]  # filter out airflow points > -0.5, since the code requirement is at this point

        # linear regression
        reg = LinearRegression(fit_intercept=False).fit(
            self.df["normalized_v_fan"].values.reshape(-1, 1),
            self.df["normalized_p_power_fan_ct"],
        )  # fit_intercept=False is for set the intercept to 0

        if reg.coef_[0] >= 1.4:
            self.df["result"] = True
        else:
            self.df["result"] = False

        self.result = self.df["result"]

    def check_detail(self) -> Dict:
        output = {
            "Sample #": 1,
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output

    def all_plot_aio(self, plt_pts):
        pass

    def all_plot_obo(self, plt_pts):
        pass

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
