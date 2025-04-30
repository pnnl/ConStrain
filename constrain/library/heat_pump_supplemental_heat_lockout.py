"""
### Description

Section 6.4.3.5 Heat Pump Auxiliary Heat Control
- Heat pumps equipped with internal electric resistance heaters shall have controls that prevent supplemental heater operation when the heating load can be met by the heat pump alone during both steady-state operation and setback recovery. Supplemental heater operation is permitted during outdoor coil defrost cycles.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3.5 Heat Pump Auxiliary Heat Control & 6.3.2.h Criteria

### Verification Approach

The verification checks three conditions:
1. If heating coil is off: always pass
2. If defrost cycle is active: always pass
3. Otherwise: supplemental heat only allowed when heat pump capacity is below load
   - Capacity calculated using reference capacity with temperature and flow modifiers

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): heat pumps with supplemental heating
- Climate Zone(s): any
- Component(s): heat pumps, supplemental heaters, defrost controls

### Verification Algorithm Pseudo Code

```python
operating_capacity = capacity_full_load * capacity_modifier_temperature * capacity_modifier_fraction_flow

if power_heating_supplemental == 0:
    pass
elif load_defrost > 0:
    pass
elif operating_capacity > load_operation:
    fail 
else:
    pass  
```

### Data requirements

- capacity_full_load: Heating coil reference capacity
  - Data Value Unit: power
  - Data Point Affiliation: Equipment specifications

- load_operation: Heating coil runtime fraction
  - Data Value Unit: fraction
  - Data Point Affiliation: System monitoring

- capacity_modifier_temperature: Temperature capacity modifier
  - Data Value Unit: fraction
  - Data Point Affiliation: Equipment performance

- power_heating_supplemental: Supplemental heating power
  - Data Value Unit: power
  - Data Point Affiliation: System monitoring

- capacity_modifier_fraction_flow: Heating capacity function of flow fraction curve
  - Data Value Unit: fraction
  - Data Point Affiliation: Equipment performance

- load_defrost: Defrost load on the heating coil
  - Data Value Unit: power
  - Data Point Affiliation: System operation

"""

from constrain.checklib import RuleCheckBase


class HeatPumpSupplementalHeatLockout(RuleCheckBase):
    points = [
        "capacity_full_load",
        "load_operation",
        "power_heating_supplemental",
        "capacity_modifier_temperature",
        "capacity_modifier_fraction_flow",
        "load_defrost",
    ]

    def heating_coil_verification(self, data):
        if data["power_heating_supplemental"] == 0:
            data["result"] = 1  # True
        else:
            if data["load_defrost"] > 0:
                data["result"] = 1
            else:
                if data["C_op"] > (
                    data["load_operation"] + self.get_tolerance("load", "general")
                ):
                    data["result"] = 0  # False
                else:
                    data["result"] = 1
        return data

    def verify(self):
        self.df["C_op"] = (
            self.df["capacity_full_load"]
            * self.df["capacity_modifier_temperature"]
            * self.df["capacity_modifier_fraction_flow"]
        )
        self.df["result"] = "Untested"
        self.df = self.df.apply(lambda r: self.heating_coil_verification(r), axis=1)
        self.result = self.df["result"]
