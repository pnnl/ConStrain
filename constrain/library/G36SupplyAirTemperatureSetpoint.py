"""
### Description

This verification aims to check if the supply air temperature setpoint is properly calculated based on system operation mode and outdoor air conditions. The setpoint should adjust according to specific rules for each mode while maintaining appropriate limits.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
- Code Subsection: 5.16.2.3 Supply Air Temperature Control

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
if t_max > max_clg_sa_t_sp:
    fail

# Calculate setpoint based on mode
match operation_mode:
    case "cooldown":
        sa_t_sp = min_clg_sa_t_sp
    case "warmup" | "setback":
        sa_t_sp = 35.0  # 95°F
    case "occupied" | "setup":
        if oa_t <= oa_t_min:
            sa_t_sp = t_max
        elif oa_t >= oa_t_max:
            sa_t_sp = min_clg_sa_t_sp
        else:
            # Linear interpolation
            sa_t_sp = (oa_t - oa_t_min) * (t_max - min_clg_sa_t_sp) / (oa_t_min - oa_t_max) + t_max

# Verify setpoint matches calculated value
if abs(sa_t_sp - sa_t_sp_ac) < sa_sp_tol:
    pass
else:
    fail
```

### Data requirements

- operation_mode: System operation mode
  - Data Value Unit: enumeration
  - Data point Description: Current system operation mode
  - Data Point Affiliation: System control

- t_max: Maximum temperature
  - Data Value Unit: °C
  - Data point Description: Maximum allowable supply air temperature
  - Data Point Affiliation: System configuration

- max_clg_sa_t_sp: Maximum cooling setpoint
  - Data Value Unit: °C
  - Data point Description: Maximum cooling supply air temperature setpoint
  - Data Point Affiliation: System configuration

- min_clg_sa_t_sp: Minimum cooling setpoint
  - Data Value Unit: °C
  - Data point Description: Minimum cooling supply air temperature setpoint
  - Data Point Affiliation: System configuration

- oa_t: Outdoor air temperature
  - Data Value Unit: °C
  - Data point Description: Current outdoor air temperature
  - Data Point Affiliation: Environmental conditions

- oa_t_min: Minimum outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Lower bound for outdoor air reset
  - Data Point Affiliation: System configuration

- oa_t_max: Maximum outdoor temperature
  - Data Value Unit: °C
  - Data point Description: Upper bound for outdoor air reset
  - Data Point Affiliation: System configuration

- sa_t_sp_ac: Actual setpoint
  - Data Value Unit: °C
  - Data point Description: Current active supply air temperature setpoint
  - Data Point Affiliation: System control

- sa_sp_tol: Setpoint tolerance
  - Data Value Unit: °C
  - Data point Description: Allowable deviation from calculated setpoint
  - Data Point Affiliation: System configuration

"""

from constrain.checklib import RuleCheckBase


class G36SupplyAirTemperatureSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "t_max",
        "max_clg_sa_t_sp",
        "min_clg_sa_t_sp",
        "oa_t",
        "oa_t_min",
        "oa_t_max",
        "sa_t_sp_ac",
        "sa_sp_tol",
    ]

    def supply_air_temperature_setpoint(self, data):
        if data["t_max"] > data["max_clg_sa_t_sp"]:
            return False
        sa_t_sp = -999
        if data["operation_mode"] == "cooldown":
            sa_t_sp = data["min_clg_sa_t_sp"]
        elif data["operation_mode"] in ["warmup", "setback"]:
            sa_t_sp = 35.0  # 95 deg. F
        elif data["operation_mode"] in ["occupied", "setup"]:
            if data["oa_t"] <= data["oa_t_min"]:
                sa_t_sp = data["t_max"]
            elif data["oa_t"] >= data["oa_t_max"]:
                sa_t_sp = data["min_clg_sa_t_sp"]
            else:
                sa_t_sp = (data["oa_t"] - data["oa_t_min"]) * (
                    data["t_max"] - data["min_clg_sa_t_sp"]
                ) / (data["oa_t_min"] - data["oa_t_max"]) + data["t_max"]
        if sa_t_sp == -999:
            return "Untested"
        if abs(sa_t_sp - data["sa_t_sp_ac"]) < data["sa_sp_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.supply_air_temperature_setpoint(d), axis=1
        )
