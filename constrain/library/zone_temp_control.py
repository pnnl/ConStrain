"""
### Description

This verification aims to check if zone temperature control maintains proper deadband between heating and cooling setpoints. The system should maintain at least 5°F (2.77°C) separation between setpoints.

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
if (cooling_setpoint - heating_setpoint) > 2.77:  # 5°F = 2.77°C
    pass
else:
    fail
```

### Data requirements

- t_z_cool_sp: Cooling setpoint
  - Data Value Unit: temperature
  - Data point Description: Zone cooling temperature setpoint
  - Data Point Affiliation: Zone control

- t_z_heat_sp: Heating setpoint
  - Data Value Unit: temperature
  - Data point Description: Zone heating temperature setpoint
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
        ) > 2.77
