"""
ASHRAE 90.1-2022
### Description

Section 6.5.3.9.1 Occupied-Standby Control of Multiple-Zone Systems

- Multi-zone systems with ventilation optimization shall reset their outdoor air setpoint assuming that all zones in standby mode don't require any outdoor air.

Verification Item:

- Check that the requested outdoor air flow rate setpoint is at least reduced by the amount of outdoor air that would be required for the zone in standby mode.

### Verification logic

In the following pseudo code `None` means that the verification is not verifiable, `True` means that it is verifiable and that the verification passes, and `False` that it fails.

```
If (zone_is_standby_mode)
  If (m_oa_requested_system[t_last_standby] - m_oa_requested_system[t]) >= m_oa_zone_requirement
    return True
  Else
    return False
  Endif
  t_last_standby = t
Else
  return None
Endif
```

### Data requirements
- zone_is_standby_mode: flag indicating whether the zone is in 'active' occupied standby mode; data can be either a boolean (True or False), or numeric boolean (0 or 1)
- m_oa_requested_by_system: system outdoor air setpoint, i.e., outdoor air required by the system for the reported period
- m_oa_zone_requirement: required zone outdoor air flow rate for the reported period

"""

from constrain.checklib import RuleCheckBase


class MZSystemOccupiedStandbyVentilationZoneControl(RuleCheckBase):
    points = [
        "zone_is_standby_mode",
        "m_oa_requested_by_system",
        "m_oa_zone_requirement",
    ]
    last_non_standby_mode_requested_m_oa = None  # expects kg/s

    def occupied_standby_ventilation_zontrol_control(self, data):
        # initialization
        if self.last_non_standby_mode_requested_m_oa is None:
            self.last_non_standby_mode_requested_m_oa = data["m_oa_requested_by_system"]
        # verification
        if data["zone_is_standby_mode"]:
            if (
                self.last_non_standby_mode_requested_m_oa
                - data["m_oa_requested_by_system"]
            ) >= data["m_oa_zone_requirement"]:
                return True
            else:
                return False
        else:
            self.last_non_standby_mode_requested_m_oa = data["m_oa_requested_by_system"]
            return "Untested"

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.occupied_standby_ventilation_zontrol_control(d), axis=1
        )
