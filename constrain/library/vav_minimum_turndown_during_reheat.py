"""
### Description

This verification aims to check if VAV boxes maintain proper minimum turndown ratios during reheat operation. The system should limit airflow to prevent excessive simultaneous heating and cooling while ensuring adequate ventilation.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2 Simultaneous Heating and Cooling Limitation
- Code Subsection: 6.5.2.1 Zone Controls

### Verification Approach

The verification monitors airflow during reheat operation:
1. Calculate actual turndown ratio:
   - Current flow divided by maximum flow
2. Compare to minimum design requirement:
   - Allow small tolerance in comparison
   - Pass if ratio stays below limit
   - Fail if ratio exceeds limit
3. Mark as untested when not in reheat mode

### Verification Applicability

- Building Type(s): any with VAV systems
- Space Type(s): any with reheat capability
- System(s): VAV terminal units
- Climate Zone(s): any
- Component(s): VAV boxes, reheat coils, airflow sensors

### Verification Algorithm Pseudo Code

```python
if reheat_coil_active:
    if max_flow == 0:
        untested  # Cannot calculate ratio
    elif current_flow / max_flow > min_turndown + tolerance:
        fail  # Excessive flow during reheat
    else:
        pass  # Proper turndown maintained
else:
    untested  # Not in reheat mode
```

### Data requirements

- reheat_coil_flag: Reheat status
  - Data Value Unit: boolean
  - Data point Description: Indicates if reheat coil is active
  - Data Point Affiliation: Terminal unit control

- V_dot_VAV: Current flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current VAV box airflow rate
  - Data Point Affiliation: Terminal unit monitoring

- V_dot_VAV_max: Maximum flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Maximum VAV box airflow setpoint
  - Data Point Affiliation: Terminal unit configuration

- VAV_min_turndown_design: Minimum turndown
  - Data Value Unit: fraction
  - Data point Description: Minimum allowable flow ratio
  - Data Point Affiliation: Terminal unit configuration

- turndown_tol: Flow tolerance
  - Data Value Unit: fraction
  - Data point Description: Allowable deviation from turndown ratio
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheat(RuleCheckBase):
    points = [
        "reheat_coil_flag",  # boolean
        "V_dot_VAV",  # actual VAV volume flow
        "V_dot_VAV_max",  # max VAV volume flow
        "VAV_min_turndown_design",
        "turndown_tol",
    ]

    def vav_turndown_check(self, data):
        if data["reheat_coil_flag"]:
            if data["V_dot_VAV_max"] == 0:
                return "Untested"
            elif (
                data["V_dot_VAV"] / data["V_dot_VAV_max"]
                > data["VAV_min_turndown_design"] + data["turndown_tol"]
            ):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        if (self.df["V_dot_VAV_max"] != 0).all():
            self.df["V_dot_ratio"] = (
                self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]
            )  # for plotting
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)
