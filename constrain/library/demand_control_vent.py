"""
### Description

Section 6.4.3.8 Ventilation Controls for High-Occupancy Areas
- Demand control ventilation (DCV) is required for spaces larger than 500 ft2 and with a design occupancy for ventilation of 25 people per 1000 ft2 of floor area and served by systems with one or more of the following:
a. Air economizer.
b. Automatic modulating control of outdoor air damper.
c. Design outdoor airflow greater than 3000 cfm.


### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3.8 Ventilation Controls for High-Occupancy Areas

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
df_filtered = df.loc[(df["status_economizer"] == 0.0) & (df["status_ahu"] != 0.0)]

if len(df_filtered) == 0:
    return "Untested"  # No valid samples

# Calculate correlation between occupancy and outdoor air flow
correlation, p_value = pearsonr(df_filtered["number_occupants"], df_filtered["flow_volumetric_air_outdoor"])

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

- flow_volumetric_air_outdoor: Zone Air Terminal Outdoor Air Volume Flow Rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Zone ventilation

- status_ahu: HVAC System Operation Status
  - Data Value Unit: binary
  - Data Point Affiliation: System operation

- status_economizer: Air System Outdoor Air Economizer Status
  - Data Value Unit: binary
  - Data Point Affiliation: System operation

- number_occupants: People Occupant Count
  - Data Value Unit: count
  - Data Point Affiliation: Zone occupancy

"""

import pandas as pd
from constrain.checklib import CheckLibBase
from scipy.stats import pearsonr


class DemandControlVentilation(CheckLibBase):
    points = [
        "flow_volumetric_air_outdoor",
        "status_ahu",
        "status_economizer",
        "number_occupants",
    ]

    def verify(self):
        self.bool_result = None
        df_filtered = self.df.loc[
            (self.df["status_economizer"] == 0.0) & (self.df["status_ahu"] != 0.0)
        ]  # filter out data when economizer isn't enabled

        if len(df_filtered) == 0:
            self.bool_result = "Untested"
            self.msg = (
                "There is no samples with economizer off and AHU on, result: untested"
            )
        else:
            corr, p_value = pearsonr(
                df_filtered["number_occupants"],
                df_filtered["flow_volumetric_air_outdoor"],
            )
            if p_value > 0.05:
                self.bool_result = "Untested"
                self.msg = "correlation p value too large, result: untested"
            else:
                if corr >= 0.3:
                    self.bool_result = True
                    self.msg = "positive correlation between flow_volumetric_air_outdoor and number_occupants observed, result: pass"
                elif corr < 0.3 and corr > 0:
                    self.bool_result = False
                    self.msg = "positive correlation between flow_volumetric_air_outdoor and number_occupants is too small, result: fail"
                else:
                    self.bool_result = False
                    self.msg = "negative correlation between flow_volumetric_air_outdoor and number_occupants observed, result: fail"

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
