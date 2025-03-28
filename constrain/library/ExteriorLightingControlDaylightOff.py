"""
ASHRAE 90.1-2022
### Description

Section 9.4.1.4.b Daylight OFF control

- [Exterior] Lighting shall automatically turn off when sufficient daylight is available or within 30 minutes of sunrise.

Verification Item:

- Check if the lighting power is turned off when enough daylight is available.

### Verification logic

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
- is_sun_up: flag indicating whether the sun is up; data can be either a boolean (True or False), or numeric boolean (0 or 1)
- daylight_sensed: Amount of daylight sensed by a photocell type sensor; unit should be consistent with `daylight_setpoint`
- daylight_setpoint: Setpoint or threshold below which daylight is not sufficient and exterior lighting is required
- total_lighting_power: reported total lighting power (not the design total lighting power)

"""

from constrain.checklib import RuleCheckBase
import numpy as np


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
            if data["total_lighting_power"] <= self.get_tolerance(
                "power", "exterior_lighting"
            ):
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.daylight_off(d), axis=1)
