"""
### Description

Section 6.5.2.1 ASHRAE 90.1-2016 interpretation:

- When a VAV box is in reheat mode, the average value of the ratio of actual VAV volume flow to max VAV volume flow should be higher than when it isn't in reheat mode
- When a VAV box is not in reheat mode, the average value of the ratio of actual VAV volume flow to max VAV volume flow should be lower than when it isn't in reheat mode


Verification Item 1:

- When a VAV box is in reheat mode, the ratio of V_dot_VAV to V_dot_VAV_max should be higher than when it isn't in reheat mode

### Verification logic

```python
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

"""

from constrain.checklib import RuleCheckBase


class VAVTurndown_Using_Average(RuleCheckBase):
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

        self.df["V_dot_VAV_ratio"] = self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]

        # Calculate the mean ratios for reheat and no reheat conditions
        mean_reheat_ratio = float(
            self.df.loc[self.df["reheat_coil_flag"], "V_dot_VAV_ratio"].mean()
        )
        mean_no_reheat_ratio = float(
            self.df.loc[~self.df["reheat_coil_flag"], "V_dot_VAV_ratio"].mean()
        )
        self.df["result"] = mean_reheat_ratio <= mean_no_reheat_ratio

        self.result = self.df["result"]

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
