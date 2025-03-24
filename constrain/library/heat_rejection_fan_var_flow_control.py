"""
### Description

This verification aims to check if heat rejection fan power varies appropriately with flow rate in variable flow systems. The fan power should follow a cubic relationship with flow rate to achieve energy savings at part-load conditions.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.5.5.2 Fan Control
- Code Subsection: Heat Rejection Fan Variable Flow Control

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
normalized_flow = fan_flow / design_flow
normalized_power = fan_power / design_power

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

- p_fan_ct: Fan power
  - Data Value Unit: power
  - Data point Description: Cooling tower fan power
  - Data Point Affiliation: Fan monitoring

- ratio_v_fan_ct: Flow ratio
  - Data Value Unit: fraction
  - Data point Description: Cooling tower fan flow ratio
  - Data Point Affiliation: Fan control

- p_fan_ct_dsgn: Design power
  - Data Value Unit: power
  - Data point Description: Cooling tower fan design power
  - Data Point Affiliation: Equipment specifications

- v_fan_ct_dsgn: Design flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Cooling tower fan design flow rate
  - Data Point Affiliation: Equipment specifications

"""

from typing import Dict

from constrain.checklib import RuleCheckBase
from sklearn.linear_model import LinearRegression


class HeatRejectionFanVariableFlowControl(RuleCheckBase):
    points = ["ct_P_fan", "ct_m_fan_ratio", "ct_P_fan_dsgn", "ct_m_fan_dsgn"]

    def verify(self):
        self.df["m_ct_fan"] = self.df["ct_m_fan_ratio"] * self.df["ct_m_fan_dsgn"]
        self.df["normalized_m_ct_fan"] = self.df["m_ct_fan"] / self.df["ct_m_fan_dsgn"]
        self.df["normalized_P_ct_fan"] = self.df["ct_P_fan"] / self.df["ct_P_fan_dsgn"]

        self.df = self.df.loc[
            self.df["normalized_P_ct_fan"] > 0.0
        ]  # filter out 0 values
        self.df["normalized_m_ct_fan"] -= 1  # minus 1 to transform the data
        self.df["normalized_P_ct_fan"] -= 1

        self.df = self.df.loc[
            self.df["normalized_m_ct_fan"] > -0.5
        ]  # filter out airflow points > -0.5, since the code requirement is at this point

        # linear regression
        reg = LinearRegression(fit_intercept=False).fit(
            self.df["normalized_m_ct_fan"].values.reshape(-1, 1),
            self.df["normalized_P_ct_fan"],
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
