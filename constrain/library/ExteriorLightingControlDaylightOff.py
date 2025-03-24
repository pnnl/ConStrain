"""
### Description

This verification aims to check if exterior lighting control operates correctly based on daylight availability. The system should automatically turn off exterior lighting when sufficient daylight is available or within 30 minutes of sunrise.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2022
- Code Section: 9.4.1.4 Exterior Lighting Control
- Code Subsection: 9.4.1.4.b Daylight OFF control

### Verification Approach

The verification checks if the exterior lighting is turned off when either sufficient daylight is detected by sensors or within 30 minutes after sunrise. The verification passes if the lighting power is zero under these conditions.

### Verification Applicability

- Building Type(s): any
- Space Type(s): exterior spaces
- System(s): exterior lighting systems
- Climate Zone(s): any
- Component(s): lighting controls, daylight sensors

### Verification Algorithm Pseudo Code

```
daylight_setpoint_met = data["v_daylight_sensed"] / data["sp_daylight"]

If daylight_setpoint_met >= 1 or time_since_last_sun_up >= 30: # min
    If p_light_total == 0:
        Pass
    Else
        Fail
    Endif
Else
    Untested
Endif
```

### Data requirements

- flag_sun_up: Sun position flag
  - Data Value Unit: binary
  - Data point Description: Sun position flag
  - Data Point Affiliation: Environmental conditions

- v_daylight_sensed: Measured daylight level
  - Data Value Unit: illuminance
  - Data point Description: Measured daylight level
  - Data Point Affiliation: Lighting control

- sp_daylight: Daylight threshold
  - Data Value Unit: illuminance
  - Data point Description: Daylight setpoint
  - Data Point Affiliation: Lighting control

- p_light_total: Lighting power
  - Data Value Unit: power
  - Data point Description: Total lighting power
  - Data Point Affiliation: Lighting system

"""

from constrain.checklib import RuleCheckBase


class ExteriorLightingControlDaylightOff(RuleCheckBase):
    points = [
        "is_sun_up",
        "daylight_sensed",
        "daylight_setpoint",
        "total_lighting_power",
    ]
    last_sun_up_time = None
    was_sun_up = False

    def daylight_off(self, data):
        # determine the time between now and the last time the sun rose
        if data["is_sun_up"] and not self.was_sun_up:
            self.last_sun_up_time = data.name
        elif self.last_sun_up_time is None:  # initialization
            self.last_sun_up_time = data.name
        diff_since_last_sun_up = data.name - self.last_sun_up_time
        time_since_last_sun_up = diff_since_last_sun_up.total_seconds() / 60
        self.was_sun_up = data["is_sun_up"]

        # determine if enough daylight is sensed
        daylight_setpoint_met = data["daylight_sensed"] / data["daylight_setpoint"]

        # perform verification
        if daylight_setpoint_met >= 1 or time_since_last_sun_up >= 30:
            if data["total_lighting_power"] == 0:
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.daylight_off(d), axis=1)
