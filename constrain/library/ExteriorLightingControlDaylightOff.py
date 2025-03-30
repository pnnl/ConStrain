"""
### Description

Section 9.4.1.4.b Daylight OFF control
- [Exterior] Lighting shall automatically turn off when sufficient daylight is available or within 30 minutes of sunrise.

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
daylight_setpoint_met = data["value_daylight"] / data["value_daylight_setpoint"]

If daylight_setpoint_met >= 1 or time_since_last_sun_up >= 30: # min
    If power_light_total == 0:
        Pass
    Else
        Fail
    Endif
Else
    Untested
Endif
```

### Data requirements

- flag_sun_up: Flag indicating whether the sun is up; data can be either a boolean (True or False), or numeric boolean (0 or 1)
  - Data Value Unit: binary
  - Data Point Affiliation: Environmental conditions

- value_daylight: Amount of daylight sensed by a photocell type sensor; unit should be consistent with `daylight_setpoint`
  - Data Value Unit: illuminance
  - Data Point Affiliation: Lighting control

- value_daylight_setpoint: Setpoint or threshold below which daylight is not sufficient and exterior lighting is required
  - Data Value Unit: illuminance
  - Data Point Affiliation: Lighting control

- power_light_total: Reported total lighting power (not the design total lighting power)
  - Data Value Unit: power
  - Data Point Affiliation: Lighting system

"""

from constrain.checklib import RuleCheckBase


class ExteriorLightingControlDaylightOff(RuleCheckBase):
    points = [
        "flag_sun_up",
        "value_daylight",
        "value_daylight_setpoint",
        "power_light_total",
    ]
    last_sun_up_time = None
    was_sun_up = False

    def daylight_off(self, data):
        # determine the time between now and the last time the sun rose
        if data["flag_sun_up"] and not self.was_sun_up:
            self.last_sun_up_time = data.name
        elif self.last_sun_up_time is None:  # initialization
            self.last_sun_up_time = data.name
        diff_since_last_sun_up = data.name - self.last_sun_up_time
        time_since_last_sun_up = diff_since_last_sun_up.total_seconds() / 60
        self.was_sun_up = data["flag_sun_up"]

        # determine if enough daylight is sensed
        daylight_setpoint_met = data["value_daylight"] / data["value_daylight_setpoint"]

        # perform verification
        if daylight_setpoint_met >= 1 or time_since_last_sun_up >= 30:
            if data["power_light_total"] <= self.get_tolerance(
                "power", "lighting_exterior"
            ):
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.daylight_off(d), axis=1)
