"""
### Description

This verification aims to check if the terminal box heating coil maintains the minimum discharge air temperature requirement during occupied mode. The heating coil should modulate to prevent the discharge air temperature from falling below the specified minimum.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.6.5 Terminal Box Airflow Control with Reheat
- Code Subsection: 5.6.5.4 Heating Coil Minimum Temperature Control

### Verification Approach

The verification checks that during occupied mode, if the discharge air temperature falls below 10°C, the heating coil should be at maximum output (trying its best to maintain temperature). If the temperature is below minimum and the coil is not at maximum, this indicates a control failure.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): VAV terminal boxes with reheat
- Climate Zone(s): any
- Component(s): terminal box controllers, heating coils, temperature sensors

### Verification Algorithm Pseudo Code

```python
if operation_mode != 'occupied':
    untested
else:
    if dat < 10 and heating_coil_command < 99:
        fail
    else:
        pass
```

### Data requirements

- operation_mode: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: Current operation mode of the system
  - Data Point Affiliation: System control

- heating_coil_command: Heating coil command
  - Data Value Unit: percent (0-100)
  - Data point Description: Current heating coil control signal
  - Data Point Affiliation: Terminal box control

- dat: Discharge air temperature
  - Data Value Unit: °C
  - Data point Description: Current discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxHeatingCoilLowerBound(RuleCheckBase):
    points = [
        "operation_mode",
        "heating_coil_command",
        "dat",
    ]

    def heating_coil_working(self, operation_mode, heating_coil_command, dat):
        if operation_mode.lower().strip() != "occupied":
            return "Untested"
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
