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
daylight_setpoint_met = data["daylight_sensed"] / data["daylight_setpoint"]

If daylight_setpoint_met >= 1 or time_since_last_sun_up >= 30: # min
    If total_lighting_power == 0:
        Pass
    Else
        Fail
    Endif
Else
    Untested
Endif
```

### Data requirements

- is_sun_up: Sun position flag
  - Data Value Unit: boolean or binary (0/1)
  - Data point Description: Flag indicating whether the sun is up
  - Data Point Affiliation: Environmental conditions

- daylight_sensed: Measured daylight level
  - Data Value Unit: consistent with daylight_setpoint
  - Data point Description: Amount of daylight sensed by photocell sensor
  - Data Point Affiliation: Lighting control

- daylight_setpoint: Daylight threshold
  - Data Value Unit: consistent with daylight_sensed
  - Data point Description: Threshold below which daylight is insufficient
  - Data Point Affiliation: Lighting control

- total_lighting_power: Lighting power
  - Data Value Unit: power
  - Data point Description: Total exterior lighting power consumption
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
