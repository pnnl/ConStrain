"""
### Description

This verification aims to check if the supply air temperature setpoint is properly calculated based on system operation mode and outdoor air conditions. The setpoint should adjust according to specific rules for each mode while maintaining appropriate limits.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
- Code Subsection: 5.16.2.2 Supply Air Temperature Setpoint

### Verification Approach

The verification checks supply air temperature setpoint calculation in multiple steps:
1. Verify maximum temperature limit is not exceeded
2. Calculate setpoint based on operation mode:
   - Cooldown: Use minimum cooling setpoint
   - Warmup/Setback: Use fixed high temperature (35°C/95°F)
   - Occupied/Setup: Calculate based on outdoor air temperature using linear reset
3. Verify actual setpoint matches calculated value within tolerance

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Air handling units
- Climate Zone(s): any
- Component(s): supply air temperature sensors, control sequences

### Verification Algorithm Pseudo Code

```python
# First check maximum temperature limit
if t_sa_max > t_sa_cool_max:
    fail

# Calculate setpoint based on mode
match mode_sys:
    case "cooldown":
        t_sa_sp_calc = t_sa_cool_min
    case "warmup" | "setback":
        t_sa_sp_calc = 35.0  # 95°F
    case "occupied" | "setup":
        if t_oa <= t_oa_min:
            t_sa_sp_calc = t_sa_max
        elif t_oa >= t_oa_max:
            t_sa_sp_calc = t_sa_cool_min
        else:
            # Linear interpolation
            t_sa_sp_calc = (t_oa - t_oa_min) * (t_sa_max - t_sa_cool_min) / (t_oa_min - t_oa_max) + t_sa_max

# Verify setpoint matches calculated value
if abs(t_sa_sp_calc - sp_t_sa) < tol_t_sa:
    pass
else:
    fail
```

### Data requirements

- mode_operation: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: System mode
  - Data Point Affiliation: System control

- t_sa_max: Maximum supply air temperature
  - Data Value Unit: temperature
  - Data point Description: Maximum supply air temperature
  - Data Point Affiliation: System configuration

- t_sa_cool_max: Maximum cooling supply air temperature
  - Data Value Unit: temperature
  - Data point Description: Maximum cooling supply air temperature
  - Data Point Affiliation: System configuration

- t_sa_cool_min: Minimum cooling supply air temperature
  - Data Value Unit: temperature
  - Data point Description: Minimum cooling supply air temperature
  - Data Point Affiliation: System configuration

- t_oa: Outdoor air temperature
  - Data Value Unit: temperature
  - Data point Description: Outdoor air temperature
  - Data Point Affiliation: Environmental conditions

- t_oa_min: Minimum outdoor air temperature
  - Data Value Unit: temperature
  - Data point Description: Minimum outdoor air temperature
  - Data Point Affiliation: System configuration

- t_oa_max: Maximum outdoor air temperature
  - Data Value Unit: temperature
  - Data point Description: Maximum outdoor air temperature
  - Data Point Affiliation: System configuration

- t_sa_sp: Supply air temperature setpoint
  - Data Value Unit: temperature
  - Data point Description: Supply air temperature setpoint
  - Data Point Affiliation: System control

- tol_t_sa: Supply air temperature tolerance
  - Data Value Unit: temperature
  - Data point Description: Supply air temperature tolerance
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class G36SupplyAirTemperatureSetpoint(RuleCheckBase):
    points = [
        "mode_operation",
        "t_sa_max",
        "t_sa_cool_max",
        "t_sa_cool_min",
        "t_oa",
        "t_oa_min",
        "t_oa_max",
        "t_sa_sp",
        "tol_t_sa",
    ]

    def supply_air_temperature_setpoint(self, data):
        if data["t_sa_max"] > data["t_sa_cool_max"]:
            return False
        sa_t_sp = -999
        if data["mode_operation"] == "cooldown":
            sa_t_sp = data["t_sa_cool_min"]
        elif data["mode_operation"] in ["warmup", "setback"]:
            sa_t_sp = 35.0  # 95 deg. F
        elif data["mode_operation"] in ["occupied", "setup"]:
            if data["t_oa"] <= data["t_oa_min"]:
                sa_t_sp = data["t_sa_max"]
            elif data["t_oa"] >= data["t_oa_max"]:
                sa_t_sp = data["t_sa_cool_min"]
            else:
                sa_t_sp = (data["t_oa"] - data["t_oa_min"]) * (
                    data["t_sa_max"] - data["t_sa_cool_min"]
                ) / (data["t_oa_min"] - data["t_oa_max"]) + data["t_sa_max"]
        if sa_t_sp == -999:
            return "Untested"
        if abs(sa_t_sp - data["t_sa_sp"]) < data["tol_t_sa"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.supply_air_temperature_setpoint(d), axis=1
        )
