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
if not economizer_lockout(t_oa, t_oa_econ_hl) and mode_sys == 'occupied':
    if pos_damper_oa >= pos_damper_oa_min and v_oa >= v_oa_min:
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

- t_oa_econ_hl: Economizer high limit temperature
  - Data Value Unit: °C
  - Data point Description: Economizer high limit temperature
  - Data Point Affiliation: Economizer control

- pos_damper_oa: Outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Outdoor air damper position
  - Data Point Affiliation: Air handling unit

- pos_damper_oa_min: Minimum outdoor air damper position
  - Data Value Unit: percent (0-100)
  - Data point Description: Minimum outdoor air damper position
  - Data Point Affiliation: Air handling unit

- v_oa_min: Minimum outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Minimum outdoor airflow
  - Data Point Affiliation: Air handling unit

- v_oa: Outdoor airflow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Outdoor airflow
  - Data Point Affiliation: Air handling unit

- mode_sys: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System operation mode
  - Data Point Affiliation: System control

"""

from datetime import datetime

import numpy as np
import pandas as pd
from constrain.checklib import RuleCheckBase


class G36MinOAwEconomizer(RuleCheckBase):
    points = [
        "outdoor_air_temp",
        "economizer_high_limit_sp",
        "outdoor_damper_command",
        "min_oa_p",
        "outdoor_air_flow",
        "min_oa_sp",
        "sys_mode",
    ]

    def economizer_lockout(self, outdoor_air_temp, economizer_high_limit_sp):
        if outdoor_air_temp > economizer_high_limit_sp:
            return True
        else:
            return False

    def ts_verify_logic(self, t):
        if (
            not self.economizer_lockout(
                t["outdoor_air_temp"], t["economizer_high_limit_sp"]
            )
        ) and (t["sys_mode"].strip().lower() == "occupied"):
            if (t["outdoor_damper_command"] >= t["min_oa_p"]) and (
                t["outdoor_air_flow"] >= t["min_oa_sp"]
            ):
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda t: self.ts_verify_logic(t), axis=1)
