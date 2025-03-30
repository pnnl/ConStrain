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

The verification checks two conditions during reheat operation:
1. Airflow turndown ratio:
   - Calculate actual ratio (current flow / maximum flow)
   - Compare to minimum design turndown requirement
   - Allow small tolerance in comparison
2. Pressure setpoint stability:
   - Track changes in duct pressure setpoint
   - Verify setpoint remains constant during reheat
   - Allow small tolerance for measurement noise

### Verification Applicability

- Building Type(s): any with VAV systems
- Space Type(s): any with reheat capability
- System(s): VAV terminal units
- Climate Zone(s): any
- Component(s): VAV boxes, reheat coils, pressure sensors

### Verification Algorithm Pseudo Code

```python
if flag_coil_reheat:
  if flow_volumetric_air_max == 0:
     Untested
  if flow_volumetric_air_max > 0.0 and flow_volumetric_air_vav / flow_volumetric_air_max > ratio_turndown_min:
    if p_press_duct_sp_prev is None:
        Untested
    elif abs(pressure_duct_setpoint - p_press_duct_sp_prev) = 0:
        Untested
    else:
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

- pressure_duct_setpoint: Duct static pressure setpoint
  - Data Value Unit: pressure
  - Data Point Affiliation: System control

"""

import numpy as np
from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheatPressureReset(RuleCheckBase):
    points = [
        "flag_coil_reheat",
        "flow_volumetric_air_vav",
        "flow_volumetric_air_max",
        "ratio_turndown_min",
        "pressure_duct_setpoint",
    ]

    def vav_turndown_check(self, data):
        if data["flag_coil_reheat"]:
            if data["flow_volumetric_air_max"] == 0:
                return "Untested"
            elif data["flow_volumetric_air_vav"] / data[
                "flow_volumetric_air_max"
            ] > data["ratio_turndown_min"] + self.get_tolerance("ratio", "flow"):
                if data["p_press_duct_sp_prev"] is None:
                    return "Untested"
                elif abs(
                    data["pressure_duct_setpoint"] - data["p_press_duct_sp_prev"]
                ) > self.get_tolerance("pressure", "static"):
                    return "Untested"
                else:
                    return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        # Copy the previous row's value in 'p_press_duct_sp' column to the current row
        self.df["p_press_duct_sp_prev"] = (
            self.df["pressure_duct_setpoint"].shift(1).replace({np.nan: None})
        )
        if (self.df["flow_volumetric_air_max"] != 0).all():
            self.df["v_vav_ratio"] = (
                self.df["flow_volumetric_air_vav"] / self.df["flow_volumetric_air_max"]
            )  # for plotting
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)
