"""
### Description

This verification aims to check if heat pump supplemental heating is properly locked out when the heat pump's capacity exceeds the heating load. Supplemental heating should only operate during defrost cycles or when the heat pump alone cannot meet the load.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.4.3.5 Heat Pump Auxiliary Heat Control
- Code Subsection: Supplemental Heat Lockout

### Verification Approach

The verification checks three conditions:
1. If supplemental heat is off: always pass
2. If defrost cycle is active: supplemental heat allowed
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
operating_capacity = reference_capacity * temperature_modifier * flow_modifier

if supplemental_heat == 0:
    pass  # No supplemental heat used
elif defrost_active > 0:
    pass  # Supplemental heat allowed during defrost
elif operating_capacity > heating_load + tolerance:
    fail  # Unnecessary supplemental heat use
else:
    pass  # Supplemental heat needed
```

### Data requirements

- cap_ref: Reference capacity
  - Data Value Unit: power
  - Data point Description: Reference capacity
  - Data Point Affiliation: Equipment specifications

- load_op: Operating load
  - Data Value Unit: power
  - Data point Description: Operating load
  - Data Point Affiliation: System monitoring

- p_htg_supp: Supplemental heat
  - Data Value Unit: power
  - Data point Description: Supplemental heating power
  - Data Point Affiliation: System monitoring

- mod_cap_t: Temperature modifier
  - Data Value Unit: fraction
  - Data point Description: Temperature capacity modifier
  - Data Point Affiliation: Equipment performance

- mod_cap_ff: Flow modifier
  - Data Value Unit: fraction
  - Data point Description: Flow capacity modifier
  - Data Point Affiliation: Equipment performance

- flag_defrost: Defrost status
  - Data Value Unit: binary
  - Data point Description: Defrost flag
  - Data Point Affiliation: System operation

- tol_cap: Capacity tolerance
  - Data Value Unit: power
  - Data point Description: Capacity tolerance
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class HeatPumpSupplementalHeatLockout(RuleCheckBase):
    points = ["C_ref", "L_op", "P_supp_ht", "C_t_mod", "C_ff_mod", "L_defrost", "tol"]

    def heating_coil_verification(self, data):
        if data["P_supp_ht"] == 0:
            data["result"] = 1  # True
        else:
            if data["L_defrost"] > 0:
                data["result"] = 1
            else:
                if data["C_op"] > data["L_op"] + data["tol"]:
                    data["result"] = 0  # False
                else:
                    data["result"] = 1
        return data

    def verify(self):
        self.df["C_op"] = self.df["C_ref"] * self.df["C_t_mod"] * self.df["C_ff_mod"]
        self.df["result"] = "Untested"
        self.df = self.df.apply(lambda r: self.heating_coil_verification(r), axis=1)
        self.result = self.df["result"]
