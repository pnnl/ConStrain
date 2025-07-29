"""
### Description

section 6.4.3.1.2 Dead Band
- Where used to control both heating and cooling, zone thermostatic controls shall be capable of and configured to provide a temperature range or dead band of at least 5°F within which the supply of heating and cooling energy to the zone is shut off or reduced to a minimum.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.4.3.1.2 Dead Band

### Verification Approach

The verification checks temperature setpoint separation:
1. Calculate deadband:
   - Difference between cooling and heating setpoints
2. Compare to minimum requirement:
   - Must exceed 5°F (2.77°C)
3. Pass if deadband meets requirement
4. Fail if deadband is insufficient

### Verification Applicability

- Building Type(s): any
- Space Type(s): any with both heating and cooling
- System(s): any zone temperature control
- Climate Zone(s): any
- Component(s): thermostats, zone controllers

### Verification Algorithm Pseudo Code

```python
if (temperature_air_zone_cool_setpoint - temperature_air_zone_heat_setpoint) > 2.77:  # 5°F = 2.77°C
    pass
else:
    fail
```

### Data requirements

- temperature_air_zone_cool_setpoint: Cooling setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: Zone control

- temperature_air_zone_heat_setpoint: Heating setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: Zone control

"""

from constrain.checklib import RuleCheckBase


class ZoneTempControl(RuleCheckBase):
    points = [
        "temperature_air_zone_cool_setpoint",
        "temperature_air_zone_heat_setpoint",
    ]

    def verify(self):
        self.result = (
            self.df["temperature_air_zone_cool_setpoint"]
            - self.df["temperature_air_zone_heat_setpoint"]
        ) > (2.77 - self.get_tolerance("temperature", "zone"))
