"""
### Description

Section 5.16.2.3
- Supply air temperature shall be controlled to setpoint using a control loop whose output is mapped to sequence the heating coil (if applicable), outdoor air damper, return air damper, and cooling coil

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
if temperature_air_supply_max > temperature_air_supply_setpoint_cool_max:
    fail

# Calculate setpoint based on mode
match mode_operation:
    case "cooldown":
        t_sa_sp_calc = temperature_air_supply_setpoint_cool_min
    case "warmup" | "setback":
        t_sa_sp_calc = 35.0  # 95°F
    case "occupied" | "setup":
        if temperature_air_outdoor <= temperature_air_outdoor_supply_min:
            t_sa_sp_calc = temperature_air_supply_max
        elif temperature_air_outdoor >= temperature_air_outdoor_supply_max:
            t_sa_sp_calc = temperature_air_supply_setpoint_cool_min
        else:
            # Linear interpolation
            t_sa_sp_calc = (temperature_air_outdoor - temperature_air_outdoor_supply_min) * (temperature_air_supply_max - temperature_air_supply_setpoint_cool_min) / (temperature_air_outdoor_supply_min - temperature_air_outdoor_supply_max) + temperature_air_supply_max

# Verify setpoint matches calculated value
if abs(t_sa_sp_calc - temperature_air_supply_setpoint) = 0:
    pass
else:
    fail
```

### Data requirements

- mode_operation: System operation mode
  - Data Value Unit: enumeration
  - Data Point Affiliation: System control

- temperature_air_supply_max: Maximum supply air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: System configuration

- temperature_air_supply_setpoint_cool_max: Maximum cooling supply air temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: System configuration

- temperature_air_supply_setpoint_cool_min: Minimum cooling supply air temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: System configuration

- temperature_air_outdoor: Outdoor air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: Environmental conditions

- temperature_air_outdoor_supply_min: Minimum outdoor air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: System configuration

- temperature_air_outdoor_supply_max: Maximum outdoor air temperature
  - Data Value Unit: temperature
  - Data Point Affiliation: System configuration

- temperature_air_supply_setpoint: Supply air temperature setpoint
  - Data Value Unit: temperature
  - Data Point Affiliation: System control

"""

from constrain.checklib import RuleCheckBase


class G36SupplyAirTemperatureSetpoint(RuleCheckBase):
    points = [
        "mode_operation",
        "temperature_air_supply_max",
        "temperature_air_supply_setpoint_cool_max",
        "temperature_air_supply_setpoint_cool_min",
        "temperature_air_outdoor",
        "temperature_air_outdoor_supply_min",
        "temperature_air_outdoor_supply_max",
        "temperature_air_supply_setpoint",
    ]

    def supply_air_temperature_setpoint(self, data):
        if (
            data["temperature_air_supply_max"]
            > data["temperature_air_supply_setpoint_cool_max"]
        ):
            return False
        sa_t_sp = -999
        if data["mode_operation"] == "cooldown":
            sa_t_sp = data["temperature_air_supply_setpoint_cool_min"]
        elif data["mode_operation"] in ["warmup", "setback"]:
            sa_t_sp = 35.0  # 95 deg. F
        elif data["mode_operation"] in ["occupied", "setup"]:
            if (
                data["temperature_air_outdoor"]
                <= data["temperature_air_outdoor_supply_min"]
            ):
                sa_t_sp = data["temperature_air_supply_max"]
            elif (
                data["temperature_air_outdoor"]
                >= data["temperature_air_outdoor_supply_max"]
            ):
                sa_t_sp = data["temperature_air_supply_setpoint_cool_min"]
            else:
                sa_t_sp = (
                    data["temperature_air_outdoor"]
                    - data["temperature_air_outdoor_supply_min"]
                ) * (
                    data["temperature_air_supply_max"]
                    - data["temperature_air_supply_setpoint_cool_min"]
                ) / (
                    data["temperature_air_outdoor_supply_min"]
                    - data["temperature_air_outdoor_supply_max"]
                ) + data[
                    "temperature_air_supply_max"
                ]
        if sa_t_sp == -999:
            return "Untested"

        if abs(sa_t_sp - data["temperature_air_supply_setpoint"]) < self.get_tolerance(
            "temperature", "supply_air"
        ):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.supply_air_temperature_setpoint(d), axis=1
        )
