"""
### Description

This verification aims to check if water-loop heat pump (WLHP) systems maintain proper temperature differential between heating and cooling loops. The system should maintain at least 20°F (11.11°C) difference between maximum heating loop temperature and minimum cooling loop temperature.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.2.2.3 Hydronic (Water Loop) Heat Pump Systems

### Verification Approach

The verification analyzes loop temperature separation:
1. During pump operation periods:
   - Track maximum heating loop temperature
   - Track minimum cooling loop temperature
2. Calculate temperature differential
3. Compare to minimum requirement:
   - Must exceed 20°F (11.11°C)
   - Allow small measurement tolerance
4. Pass if differential meets requirement

### Verification Applicability

- Building Type(s): any with WLHP systems
- Space Type(s): any
- System(s): water-loop heat pump systems
- Climate Zone(s): any
- Component(s): heat pumps, loop temperature sensors

### Verification Algorithm Pseudo Code

```python
if m_pump > 0:
    max_heating_temp = max(heating_loop_temperature)
    min_cooling_temp = min(cooling_loop_temperature)
    
    temp_differential = max_heating_temp - min_cooling_temp
    
    if temp_differential > 11.11 + tolerance:  # 20°F = 11.11°C
        pass  # Proper temperature separation
    else:
        fail  # Insufficient separation
```

### Data requirements

- t_heating_max: Heating loop temperature
  - Data Value Unit: temperature
  - Data point Description: Maximum heating loop temperature
  - Data Point Affiliation: System monitoring

- t_cooling_min: Cooling loop temperature
  - Data Value Unit: temperature
  - Data point Description: Minimum cooling loop temperature
  - Data Point Affiliation: System monitoring

- m_pump: Pump flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Pump flow rate
  - Data Point Affiliation: System monitoring

- tol_t_loop: Temperature tolerance
  - Data Value Unit: temperature
  - Data point Description: Temperature tolerance
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = [
        "temperature_water_heating_max",
        "temperature_water_cooling_min",
        "flow_mass_water_pump",
        "tol_t_loop",
    ]

    def verify(self):
        self.df["t_heating_max_max"] = (
            self.df.query("m_pump >0")["temperature_water_heating_max"]
        ).max()
        self.df["t_cooling_min_min"] = (
            self.df.query("m_pump >0")["temperature_water_cooling_min"]
        ).min()

        self.result = (
            self.df["t_heating_max_max"] - self.df["t_cooling_min_min"]
        ) > 11.11 + self.df["tol_t_loop"]
