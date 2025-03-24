"""
### Description

This verification aims to check demand control ventilation functionality for high-occupancy areas. The system should adjust outdoor air ventilation based on actual occupancy levels.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3 Controls and Diagnostics
- Code Subsection: 6.4.3.8 Demand Control Ventilation

### Verification Approach

The verification analyzes the correlation between outdoor air ventilation rates and occupancy levels when the economizer is not active. A positive correlation indicates that the ventilation rate is being adjusted based on occupancy as required.

### Verification Applicability

- Building Type(s): any
- Space Type(s): high-occupancy areas
- System(s): HVAC systems with outdoor air ventilation
- Climate Zone(s): any
- Component(s): ventilation controls, outdoor air dampers

### Verification Algorithm Pseudo Code

```
# Filter data for when economizer is off and AHU is on
df_filtered = df.loc[(df["flag_econ"] == 0.0) & (df["flag_hvac"] != 0.0)]

if len(df_filtered) == 0:
    return "Untested"  # No valid samples

# Calculate correlation between occupancy and outdoor air flow
correlation, p_value = pearsonr(df_filtered["n_occ"], df_filtered["v_oa"])

if p_value > 0.05:
    return "Untested"  # Correlation not statistically significant
elif correlation >= 0.3:
    return True  # Strong positive correlation
elif 0 < correlation < 0.3:
    return False  # Weak positive correlation
else:
    return False  # Negative correlation
```

### Data requirements

- v_oa: Zone Air Terminal Outdoor Air Volume Flow Rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Outdoor air volume flow rate
  - Data Point Affiliation: Zone ventilation

- flag_hvac: HVAC System Operation Status
  - Data Value Unit: binary
  - Data point Description: HVAC system status
  - Data Point Affiliation: System operation

- flag_econ: Air System Outdoor Air Economizer Status
  - Data Value Unit: binary
  - Data point Description: Economizer flag
  - Data Point Affiliation: System operation

- n_occ: People Occupant Count
  - Data Value Unit: count
  - Data point Description: Number of occupants
  - Data Point Affiliation: Zone occupancy

"""

import pandas as pd
from constrain.checklib import CheckLibBase
from scipy.stats import pearsonr


class DemandControlVentilation(CheckLibBase):
    points = [
        "v_oa",
        "s_ahu",
        "s_eco",
        "no_of_occ",
    ]

    def verify(self):
        self.bool_result = None
        df_filtered = self.df.loc[
            (self.df["s_eco"] == 0.0) & (self.df["s_ahu"] != 0.0)
        ]  # filter out data when economizer isn't enabled

        if len(df_filtered) == 0:
            self.bool_result = "Untested"
            self.msg = (
                "There is no samples with economizer off and AHU on, result: untested"
            )
        else:
            corr, p_value = pearsonr(df_filtered["no_of_occ"], df_filtered["v_oa"])
            if p_value > 0.05:
                self.bool_result = "Untested"
                self.msg = "correlation p value too large, result: untested"
            else:
                if corr >= 0.3:
                    self.bool_result = True
                    self.msg = "positive correlation between v_oa and no_of_occ observed, result: pass"
                elif corr < 0.3 and corr > 0:
                    self.bool_result = False
                    self.msg = "positive correlation between v_oa and no_of_occ is too small, result: fail"
                else:
                    self.bool_result = False
                    self.msg = "negative correlation between v_oa and no_of_occ observed, result: fail"

        self.result = pd.Series(data=self.bool_result, index=self.df.index)

    def check_detail(self):
        print("Verification results dict: ")
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
            "Message": self.msg,
        }
        print(output)
        return output

    def check_bool(self):
        return self.bool_result

    def day_plot_aio(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass

    def day_plot_obo(self, plt_pts):
        # This method is overwritten because day plot can't be plotted for this verification item
        pass
