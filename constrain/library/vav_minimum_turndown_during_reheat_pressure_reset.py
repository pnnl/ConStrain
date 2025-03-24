"""
### Description

This verification aims to check if VAV boxes maintain proper minimum turndown ratios during reheat operation while ensuring stable duct pressure setpoints. The system should limit airflow and maintain consistent pressure control to prevent energy waste.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2 Simultaneous Heating and Cooling Limitation
- Code Subsection: 6.5.2.1 Zone Controls

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
if flag_coil_htg:
  if v_box_max == 0:
     Untested
  if v_box_max > 0.0 and v_box / v_box_max > ratio_turndown_min + tol_turndown:
    if sp_p_press_duct_prev is None:
        Untested
    elif abs(sp_p_press_duct - sp_p_press_duct_prev) > tol_p_press:
        Untested
    else:
        fail
  else:
     pass
else: 
    Untested
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

- ratio_turndown_min: Minimum VAV turndown ratio
  - Data Value Unit: fraction
  - Data point Description: Minimum turndown ratio
  - Data Point Affiliation: Terminal unit configuration

- sp_p_duct: Duct static pressure setpoint
  - Data Value Unit: pressure
  - Data point Description: Duct pressure setpoint
  - Data Point Affiliation: System control

- tol_turndown: Turndown tolerance
  - Data Value Unit: fraction
  - Data point Description: Turndown tolerance
  - Data Point Affiliation: System configuration

- tol_p_duct: Pressure tolerance
  - Data Value Unit: pressure
  - Data point Description: Duct pressure tolerance
  - Data Point Affiliation: System configuration

"""

import numpy as np
from constrain.checklib import RuleCheckBase


class VAVMinimumTurndownDuringReheatPressureReset(RuleCheckBase):
    points = [
        "reheat_coil_flag",
        "V_dot_VAV",
        "V_dot_VAV_max",
        "VAV_min_turndown_design",
        "P_set",
        "turndown_tol",
        "P_set_tol",
    ]

    def vav_turndown_check(self, data):
        if data["reheat_coil_flag"]:
            if data["V_dot_VAV_max"] == 0:
                return "Untested"
            elif (
                data["V_dot_VAV"] / data["V_dot_VAV_max"]
                > data["VAV_min_turndown_design"] + data["turndown_tol"]
            ):
                if data["P_set_prev"] is None:
                    return "Untested"
                elif abs(data["P_set"] - data["P_set_prev"]) > data["P_set_tol"]:
                    return "Untested"
                else:
                    return False
            else:
                return True
        else:
            return "Untested"

    def verify(self):
        # Copy the previous row's value in 'P_set' column to the current row
        self.df["P_set_prev"] = self.df["P_set"].shift(1).replace({np.nan: None})
        if (self.df["V_dot_VAV_max"] != 0).all():
            self.df["V_dot_ratio"] = (
                self.df["V_dot_VAV"] / self.df["V_dot_VAV_max"]
            )  # for plotting
        self.result = self.df.apply(lambda d: self.vav_turndown_check(d), axis=1)
