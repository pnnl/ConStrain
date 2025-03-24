"""
### Description

This verification aims to check if water-loop heat pump (WLHP) systems maintain proper temperature differential between heating and cooling loops. The system should maintain at least 20°F (11.11°C) difference between maximum heating loop temperature and minimum cooling loop temperature.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.5.2.2 Hydronic System Controls
- Code Subsection: Water-Loop Heat Pump Controls

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
if pump_flow > 0:  # Only check during system operation
    max_heating_temp = max(heating_loop_temperature)
    min_cooling_temp = min(cooling_loop_temperature)
    
    temp_differential = max_heating_temp - min_cooling_temp
    
    if temp_differential > 11.11 + tolerance:  # 20°F = 11.11°C
        pass  # Proper temperature separation
    else:
        fail  # Insufficient separation
```

### Data requirements

- t_htg_max: Heating loop temperature
  - Data Value Unit: temperature
  - Data point Description: Maximum heating loop temperature
  - Data Point Affiliation: System monitoring

- t_clg_min: Cooling loop temperature
  - Data Value Unit: temperature
  - Data point Description: Minimum cooling loop temperature
  - Data Point Affiliation: System monitoring

- v_pump: Pump flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Pump flow rate
  - Data Point Affiliation: System monitoring

- tol_t: Temperature tolerance
  - Data Value Unit: temperature
  - Data point Description: Temperature tolerance
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = ["T_max_heating_loop", "T_min_cooling_loop", "m_pump", "tol"]

    def verify(self):
        self.df["T_max_heating_loop_max"] = (
            self.df.query("m_pump >0")["T_max_heating_loop"]
        ).max()
        self.df["T_min_cooling_loop_min"] = (
            self.df.query("m_pump >0")["T_min_cooling_loop"]
        ).min()

        self.result = (
            self.df["T_max_heating_loop_max"] - self.df["T_min_cooling_loop_min"]
        ) > 11.11 + self.df["tol"]
