"""
### Description

Section 5.6.5.4.
- In Occupied Mode, the heating coil shall be modulated to maintain a DAT no lower than 10°C.

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
    if temperature_air_discharge >= 10 and command_coil_heat < 100:
        fail
    else:
        pass
```

### Data requirements

- mode_system: System operation mode (if mode_system is not "occupied", this verification item falls into the "untested" result)
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- command_coil_heat: Heating coil command
  - Data Value Unit: percent
  - Data Point Affiliation: Terminal box control

- temperature_air_discharge: Discharge air temperature
  - Data Value Unit: temperature
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
        if t_discharge >= (10 - self.get_tolerance("temperature", "discharge_air")):
            return True
        else:
            if cmd_coil_heat < 100 - self.get_tolerance("damper", "command") * 100:
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
