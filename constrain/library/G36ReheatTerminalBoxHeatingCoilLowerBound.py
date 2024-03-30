"""
G36 2021
### Description

Section 5.6.5.4.

- In Occupied Mode, the heating coil shall be modulated to maintain a DAT no lower than 10°C.

### Verification logic

'''
if operation_mode != 'occupied':
    untested
if operation_mode == 'occupied':
    if dat < 10 and heating_coil_command < 99:
        fail
    else:
        pass
end
'''

### Data requirements

- operation_mode: System operation mode
- heating_coil_command: Heating coil command
- dat: Discharge air temperature

"""

from constrain.checklib import RuleCheckBase
import numpy as np
import pandas as pd


class G36ReheatTerminalBoxHeatingCoilLowerBound(RuleCheckBase):
    points = [
        "operation_mode",
        "heating_coil_command",
        "dat",
    ]

    def heating_coil_working(self, operation_mode, heating_coil_command, dat):
        if operation_mode.lower().strip() != "occupied":
            return np.nan
        if dat >= 10:
            return True
        else:
            if heating_coil_command < 99:
                return False
            else:
                return True  # heating coil tried its best

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.heating_coil_working(
                t["operation_mode"], t["heating_coil_command"], t["dat"]
            ),
            axis=1,
        )
