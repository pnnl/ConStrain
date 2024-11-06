"""
### Description
When a VAV box is in reheat mode, the ratio of V_dot_VAV to V_dot_VAV_max should be higher than when it isn't in reheat mode

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2 Simultaneous Heating and Cooling Limitation
- Code Subsection: 6.5.2.1 Zone Controls

### Verification Approach
- We aim to identify how VAV airflow rate varies when the VAV box is and isn't in reheat mode.

### Verification logic
```
V_dot_VAV_ratio = V_dot_VAV/V_dot_VAV_max
mean_reheat_ratio = df.loc[self.df[`reheat_coil_flag`], `V_dot_VAV_ratio`].mean()
mean_no_reheat_ratio = df.loc[~self.df[`reheat_coil_flag`], `V_dot_VAV_ratio`].mean()

if mean_reheat_ratio >= mean_no_reheat_ratio:
    pass
else:
    fail
```
### Data requirements
- reheat_coil_flag: VAV box reheat coil operation status
- V_dot_VAV: actual VAV volume flow
- V_dot_VAV_max: max VAV volume flow
- VAV_min_turndown_design: design VAV box min turndown ratio
- turndown_tol: VAV turndown tolerance

"""

from constrain.checklib import RuleCheckBase


class VAVTurndownDuringReheat(RuleCheckBase):
    points = [
        "reheat_coil_flag",
        "V_dot_VAV",
        "V_dot_VAV_max",
    ]

    def verify(self):
        # Make sure every value in `V_dot_VAV_max` is greater than 0
        assert (
            self.df["V_dot_VAV_max"] > 0
        ).all(), "Not all `V_dot_VAV_max` values are greater than 0"

        # Check if the `reheat_coil_flag` column has only False values
        if (self.df["reheat_coil_flag"] == False).all():
            self.df["result"] = "Untested"
        else:
            self.df["V_dot_VAV_ratio"] = self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]

            # Calculate the mean ratios for reheat and no reheat conditions
            mean_reheat_ratio = float(
                self.df.loc[self.df["reheat_coil_flag"], "V_dot_VAV_ratio"].mean()
            )
            mean_no_reheat_ratio = float(
                self.df.loc[~self.df["reheat_coil_flag"], "V_dot_VAV_ratio"].mean()
            )
            self.df["result"] = mean_reheat_ratio < mean_no_reheat_ratio

        self.result = self.df["result"]

    def check_bool(self):
        if len(self.result[self.result == "Untested"] > 0):
            return "Untested"
        elif len(self.result[self.result == False] > 0):
            return False
        else:
            return True
