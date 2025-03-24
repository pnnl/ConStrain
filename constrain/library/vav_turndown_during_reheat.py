"""
### Description

This verification aims to check if VAV boxes properly reduce airflow during reheat operation compared to normal cooling operation. The system should maintain lower airflow rates during reheat to minimize simultaneous heating and cooling.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2 Simultaneous Heating and Cooling Limitation
- Code Subsection: 6.5.2.1 Zone Controls

### Verification Approach

The verification compares average airflow ratios:
1. Calculate flow ratios (actual/maximum) for all periods
2. Separate data into reheat and non-reheat periods
3. Compare average ratios:
   - Calculate mean ratio during reheat
   - Calculate mean ratio during normal operation
   - Pass if reheat ratio is lower
4. Mark as untested if no reheat operation observed

### Verification Applicability

- Building Type(s): any with VAV systems
- Space Type(s): any with reheat capability
- System(s): VAV terminal units
- Climate Zone(s): any
- Component(s): VAV boxes, reheat coils, airflow sensors

### Verification Algorithm Pseudo Code

```python
if no_reheat_periods_exist:
    untested  # Cannot verify without reheat operation
else:
    flow_ratio = v_box / v_box_max
    
    reheat_avg = mean(flow_ratio[flag_coil_htg])
    normal_avg = mean(flow_ratio[not flag_coil_htg])
    
    if reheat_avg < normal_avg:
        pass  # Proper turndown during reheat
    else:
        fail  # Insufficient turndown
```

### Data requirements

- flag_htg_coil: VAV box reheat coil operation status
  - Data Value Unit: binary
  - Data point Description: Heating coil flag
  - Data Point Affiliation: Terminal unit control

- v_box: VAV airflow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Box volume flow rate
  - Data Point Affiliation: Terminal unit monitoring

- v_box_max: VAV maximum airflow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Box maximum volume flow rate
  - Data Point Affiliation: Terminal unit configuration

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
            mean_reheat_ratio = self.df.loc[
                self.df["reheat_coil_flag"], "V_dot_VAV_ratio"
            ].mean()
            mean_no_reheat_ratio = self.df.loc[
                ~self.df["reheat_coil_flag"], "V_dot_VAV_ratio"
            ].mean()
            self.df["result"] = mean_reheat_ratio < mean_no_reheat_ratio

        self.result = self.df["result"]
