"""
### Description

This verification aims to check if VAV boxes maintain proper minimum turndown ratios during reheat operation. The system should limit airflow to prevent excessive simultaneous heating and cooling while ensuring adequate ventilation.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2.1 Zone Controls

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
if flag_coil_htg:
  if v_vav_max == 0:
     Untested
  if v_vav_max > 0.0 and v_vav / v_vav_max > ratio_turndown_min + tol_turndown:
     fail
  else:
     pass
else: 
    Untested
```

### Data requirements

- flag_coil_reheat: VAV box reheat coil operation status
  - Data Value Unit: binary
  - Data point Description: Heating coil flag
  - Data Point Affiliation: Terminal unit control

- v_vav: VAV airflow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Box volume flow rate
  - Data Point Affiliation: Terminal unit monitoring

- v_vav_max: VAV maximum airflow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Box maximum volume flow rate
  - Data Point Affiliation: Terminal unit configuration

- ratio_turndown_min: Minimum VAV turndown ratio
  - Data Value Unit: fraction
  - Data point Description: Minimum turndown ratio
  - Data Point Affiliation: Terminal unit configuration

- tol_turndown: Turndown tolerance
  - Data Value Unit: fraction
  - Data point Description: Turndown tolerance
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheat(RuleCheckBase):
    points = [
        "flag_coil_reheat",  # boolean
        "flow_volumetric_air_vav",  # actual VAV volume flow
        "flow_volumetric_air_max",  # max VAV volume flow
        "ratio_turndown_min",
        "tol_turndown",
    ]

    def vav_turndown_check(self, data):
        if data["flag_coil_reheat"]:
            if data["flow_volumetric_air_max"] == 0:
                return "Untested"
            elif (
                data["flow_volumetric_air_vav"] / data["flow_volumetric_air_max"]
                > data["ratio_turndown_min"] + data["tol_turndown"]
            ):
                return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        if (self.df["flow_volumetric_air_max"] != 0).all():
            self.df["v_vav_ratio"] = (
                self.df["flow_volumetric_air_vav"] / self.df["flow_volumetric_air_max"]
            )  # for plotting
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)
