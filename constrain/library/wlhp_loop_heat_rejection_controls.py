"""
### Description

section 6.5.2.2.3 Hydronic (Water Loop) Heat Pump Systems
- Hydronic heat pumps connected to a common heat pump water loop with central devices for heat rejection (e.g., cooling tower) and heat addition (e.g., boiler) shall have the following:
a. Controls that are capable of and configured to provide a heat pump water supply temperature dead band of at least 20°F between initiation of heat rejection and heat addition by the central devices (e.g., tower and boiler).

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
if flow_mass_water_pump > 0:
    max_heating_temp = max(temperature_water_heating_max)
    min_cooling_temp = min(temperature_water_cooling_min)
    
    temp_differential = max_heating_temp - min_cooling_temp
    
    if temp_differential > 11.11:  # 20°F = 11.11°C
        pass  # Proper temperature separation
    else:
        fail  # Insufficient separation
```

### Data requirements

- temperature_water_heating_max: Heating loop temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: System monitoring

- temperature_water_cooling_min: Cooling loop temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: System monitoring

- flow_mass_water_pump: Pump flow
  - Data Value Unit: mass flow rate
  - Data Point Affiliation: System monitoring

"""

from constrain.checklib import RuleCheckBase


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = [
        "temperature_water_heating_max",
        "temperature_water_cooling_min",
        "flow_mass_water_pump",
    ]

    def verify(self):
        self.df["T_max_heating_loop_max"] = (
            self.df.query(
                f"flow_mass_water_pump > {self.get_tolerance('waterflow', 'general')}"
            )["temperature_water_heating_max"]
        ).max()
        self.df["T_min_cooling_loop_min"] = (
            self.df.query(
                f"flow_mass_water_pump > {self.get_tolerance('waterflow', 'general')}"
            )["temperature_water_cooling_min"]
        ).min()

        self.result = (
            self.df["T_max_heating_loop_max"] - self.df["T_min_cooling_loop_min"]
        ) > (11.11 + self.get_tolerance("temperature", "general"))
