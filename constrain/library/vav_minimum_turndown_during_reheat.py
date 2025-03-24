"""
### Description
When a VAV box is in reheat mode, the ratio of VAV airflow rate to VAV max airflow rate must not be greater than the min design turndown ratio

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2 Simultaneous Heating and Cooling Limitation
- Code Subsection: 6.5.2.1 Zone Controls

### Verification Approach
- We aim to identify how VAV airflow rate varies when the VAV box is and isn't in reheat mode.

### Verification logic
```
if reheat_coil_flag:
  if V_dot_VAV_max == 0
     Untested
  if V_dot_VAV_max > 0.0 and V_dot_VAV / V_dot_VAV_max > VAV_min_turndown_design + turndown_tol
     fail
  else:
     pass
else
    Untested
```
### Data requirements
- reheat_coil_flag: VAV box reheat coil operation status
- V_dot_VAV: actual VAV volume flow
- V_dot_VAV_max: max VAV volume flow
- VAV_min_turndown_design: design VAV box min turndown ratio

"""

from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheat(RuleCheckBase):
    points = [
        "reheat_coil_flag",  # boolean
        "V_dot_VAV",  # actual VAV volume flow
        "V_dot_VAV_max",  # max VAV volume flow
        "VAV_min_turndown_design",
    ]

    def vav_turndown_check(self, data):
        if data["reheat_coil_flag"]:
            if data["V_dot_VAV_max"] == 0:
                return "Untested"
            elif data["V_dot_VAV"] / data["V_dot_VAV_max"] > data[
                "VAV_min_turndown_design"
            ] + self.get_tolerance("ratio", "flow"):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        if (self.df["V_dot_VAV_max"] != 0).all():
            self.df["V_doret_a_temptio"] = (
                self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]
            )  # for plotting
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)
