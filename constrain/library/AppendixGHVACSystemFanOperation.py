"""
ASHRAE 90.1-2022
### Description

Section G3.1.4 HVAC System Fan Schedules

- Schedules for HVAC system fans that provide outdoor air for ventilation shall run continuously whenever spaces are occupied and shall be cycled ON and OFF to meet heating and cooling loads during unoccupied hours.

Note: exceptions to this requirement are not capture since they depend on system design which is not related to system control.

Verification Item:

- Check that when a zone is occupied and served by a system that provides outdoor air the system runs continuously and cycles when the zone is occupied.

### Verification logic

In the following pseudo code `None` means that the verification is not verifiable, `True` means that it is verifiable and that the verification passes, and `False` that it fails.

```
# Check that the system provide OA
# This is a one-time check, do not perform further checks if None is returned
If sum(m_oa) == 0
  return None
Endif

# This assumes that the system does provide OA to the space as per the first check
potential_failures_count = 0
potential_pass_count = 0
If o
  If fan_runtime_fraction == 1
    return True
  Else
    return False
  Endif
Else
  If fan_runtime_fraction == 1 # the system could be "cycling" for the whole timestep so add to counter
    potential_failures_count += 1
    return None
  Else
    potential_pass_count += 1
    return None
  Endif
Endif

# Check that if the system has been cycling for a whole timestep it also cycles during some
# If it hasn't we assume that the system is set to run continuously when the zone is unoccupied
# This is a one-time check, it can be used to make a final pass/fail decision
If potential_failures_count > 0 and potential_pass_count == 0
  return False
Endif
```

### Data requirements
- o: number of occupants sensed in the zones served by the system.
- fan_runtime_fraction: system fan runtime fraction (between 0 and 1).
- m_oa: system outdoor air flow rate.
- tol_o: occupancy threshold; below that value the zones are considered unoccupied.

"""

from constrain.checklib import RuleCheckBase


class AppendixGHVACSystemFanOperation(RuleCheckBase):
    points = ["o", "fan_runtime_fraction", "m_oa", "tol_o"]
    potential_failures_counter = 0
    potential_pass_count = 0

    def hvac_system_fan_operation(self, data):
        if data["o"] >= data["tol_o"]:
            if data["fan_runtime_fraction"] == 1:
                return True
            else:
                return False
        else:
            # the system could be "cycling" for the whole timestep
            if data["fan_runtime_fraction"] == 1:
                self.potential_failures_counter += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool
            else:
                self.potential_pass_count += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool

    def check_system_oa(self, data):
        # check that the system does provide outdoor air
        total_oa = sum(data["m_oa"])
        if total_oa > 0:
            return True
        else:
            return False

    def check_bool(self) -> bool:
        if self.check_system_oa(self.df):
            if self.potential_failures_counter > 0 and self.potential_pass_count == 0:
                return False
            else:
                return True
        else:
            return None  # untested

    def verify(self):
        if self.check_system_oa(self.df):
            self.result = self.df.apply(
                lambda d: self.hvac_system_fan_operation(d), axis=1
            )
        else:
            self.result = self.df.apply(lambda d: "Untested", axis=1)
