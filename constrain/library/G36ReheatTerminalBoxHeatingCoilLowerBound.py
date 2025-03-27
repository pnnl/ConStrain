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
if mode_system != 'occupied':
    untested
else:
    if t_discharge < 10 and cmd_coil_heat < 99:
        fail
    else:
        pass
```

### Data requirements

- mode_system: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System mode
  - Data Point Affiliation: System control

- cmd_coil_heat: Heating coil command
  - Data Value Unit: percent
  - Data point Description: Heating coil command
  - Data Point Affiliation: Terminal box control

- t_discharge: Discharge air temperature
  - Data Value Unit: temperature
  - Data point Description: Discharge air temperature
  - Data Point Affiliation: Terminal box monitoring

"""

from constrain.checklib import RuleCheckBase


class G36ReheatTerminalBoxHeatingCoilLowerBound(RuleCheckBase):
    points = [
        "mode_system",
        "command_coil_heat",
        "temperature_air_discharge",
    ]

    def heating_coil_working(self, mode_system, cmd_coil_heat, t_discharge):
        if mode_system.lower().strip() != "occupied":
            return "Untested"
        if t_discharge >= 10:
            return True
        else:
            if cmd_coil_heat < 99:
                return False
            else:
                return True  # heating coil tried its best

    def verify(self):
        self.result = self.df.apply(
            lambda t: self.heating_coil_working(
                t["mode_system"], t["command_coil_heat"], t["temperature_air_discharge"]
            ),
            axis=1,
        )
