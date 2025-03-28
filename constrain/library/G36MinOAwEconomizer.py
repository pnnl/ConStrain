"""
### Description

This verification aims to check if the minimum outdoor air control operates correctly when the economizer is active. The system should maintain outdoor air flow above minimum requirements while allowing the economizer to modulate for free cooling.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16 Air Handling Unit and Relief Fan Control Sequences
- Code Subsection: Minimum Outdoor Air Control with Economizer

### Verification Approach

The verification checks that during occupied periods when economizer is not in lockout, the outdoor air damper position and flow rate remain at or above their minimum setpoints. The actual damper modulation for temperature control is handled by the supply air temperature control loop.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units with economizers
- Climate Zone(s): any
- Component(s): outdoor air dampers, airflow sensors

### Verification Algorithm Pseudo Code

```python
if not economizer_lockout(t_oa, t_economizer_limit) and mode_system == 'occupied':
    if pos_damper_oa >= pos_damper_oa_min and v_oa >= v_oa_min_sp:
        pass
    else:
        fail
else:
    untested
```

### Data requirements

- t_oa: Outdoor air temperature
  - Data Value Unit: °C
  - Data point Description: Outdoor air temperature
  - Data Point Affiliation: Environmental conditions

- t_economizer_limit: Economizer high limit temperature
  - Data Value Unit: °C
  - Data point Description: Economizer high limit temperature
  - Data Point Affiliation: Economizer control

- pos_damper_oa: Outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Outdoor air damper command
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_min: Minimum outdoor air damper command
  - Data Value Unit: percent
  - Data point Description: Minimum outdoor air damper command
  - Data Point Affiliation: Air handling unit

- v_oa_min_sp: Minimum outdoor airflow setpoint
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum outdoor airflow setpoint
  - Data Point Affiliation: Air handling unit

- v_oa: Outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Outdoor airflow
  - Data Point Affiliation: Air handling unit

- mode_system: System mode
  - Data Value Unit: enumeration
  - Data point Description: System mode
  - Data Point Affiliation: System control

"""

from datetime import datetime

import numpy as np
import pandas as pd
from constrain.checklib import RuleCheckBase


class G36MinOAwEconomizer(RuleCheckBase):
    points = [
        "temperature_air_outdoor",
        "temperature_air_economizer_limit",
        "position_damper_air_outdoor",
        "position_damper_air_outdoor_min",
        "flow_volumetric_air_outdoor",
        "flow_volumetric_air_outdoor_setpoint_min",
        "mode_system",
    ]

    def economizer_lockout(self, t_oa, t_economizer_limit):
        if t_oa > t_economizer_limit:
            return True
        else:
            return False

    def ts_verify_logic(self, t):
        if (
            not self.economizer_lockout(
                t["temperature_air_outdoor"], t["temperature_air_economizer_limit"]
            )
        ) and (t["mode_system"].strip().lower() == "occupied"):
            if (
                t["position_damper_air_outdoor"]
                >= t["position_damper_air_outdoor_min"]
                - self.get_tolerance("damper", "position")
            ) and (
                t["flow_volumetric_air_outdoor"]
                >= t["flow_volumetric_air_outdoor_setpoint_min"]
                - self.get_tolerance("airflow", "outdoor_air")
            ):
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)
