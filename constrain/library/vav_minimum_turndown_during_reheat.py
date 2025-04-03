"""
### Description

Section 6.5.2.1 Zone Controls
- Zone thermostatic controls shall prevent
a. reheating;
b. recooling;
c. mixing or simultaneously supplying air that has been previously mechanically heated and air that has been previously cooled, either by mechanical cooling or by economizer systems; 
d. other simultaneous operation of heating and cooling systems to the same zone.

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
if flag_coil_reheat:
  if flow_volumetric_air_max == 0:
     Untested
  if flow_volumetric_air_max > 0.0 and flow_volumetric_air_vav / flow_volumetric_air_max > ratio_turndown_min:
     fail
  else:
     pass
else: 
    Untested
```

### Data requirements

- flag_coil_reheat: VAV box reheat coil operation flag
  - Data Value Unit: binary
  - Data Point Affiliation: Terminal unit control

- flow_volumetric_air_vav: VAV airflow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Terminal unit monitoring

- flow_volumetric_air_max: VAV maximum airflow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Terminal unit configuration

- ratio_turndown_min: Minimum VAV turndown ratio
  - Data Value Unit: fraction
  - Data Point Affiliation: Terminal unit configuration

"""

from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheat(RuleCheckBase):
    points = [
        "flag_coil_reheat",  # boolean
        "flow_volumetric_air_vav",  # actual VAV volume flow
        "flow_volumetric_air_max",  # max VAV volume flow
        "ratio_turndown_min",
    ]

    def vav_turndown_check(self, data):
        if data["flag_coil_reheat"]:
            if data["flow_volumetric_air_max"] == 0:
                return "Untested"
            elif data["flow_volumetric_air_vav"] / data[
                "flow_volumetric_air_max"
            ] > data["ratio_turndown_min"] + self.get_tolerance("ratio", "flow"):
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
