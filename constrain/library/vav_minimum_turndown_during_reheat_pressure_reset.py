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
if reheat_coil_active:
    if max_flow == 0:
        untested  # Cannot calculate ratio
    elif current_flow / max_flow > min_turndown + tolerance:
        if previous_pressure is None:
            untested  # Need pressure history
        elif abs(current_pressure - previous_pressure) > pressure_tolerance:
            untested  # Pressure not stable
        else:
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

- P_set: Pressure setpoint
  - Data Value Unit: pressure
  - Data point Description: Current duct static pressure setpoint
  - Data Point Affiliation: System control

- turndown_tol: Flow tolerance
  - Data Value Unit: fraction
  - Data point Description: Allowable deviation from turndown ratio
  - Data Point Affiliation: System configuration

- P_set_tol: Pressure tolerance
  - Data Value Unit: pressure
  - Data point Description: Allowable pressure setpoint variation
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
