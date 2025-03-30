"""
### Description

Section G3.1.4 HVAC System Fan Schedules
- Schedules for HVAC system fans that provide outdoor air for ventilation shall run continuously whenever spaces are occupied and shall be cycled ON and OFF to meet heating and cooling loads during unoccupied hours.
Note: exceptions to this requirement are not capture since they depend on system design which is not related to system control.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2022
- Code Section: G3.1.4 HVAC System Fan Schedules
- Code Subsection: N/A

### Verification Approach

The verification checks if the system provides outdoor air and then verifies that when a zone is occupied and served by a system that provides outdoor air, the system runs continuously. During unoccupied periods, the system should cycle on/off rather than run continuously.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): HVAC systems with outdoor air ventilation
- Climate Zone(s): any
- Component(s): system fans

### Verification Algorithm Pseudo Code

```
# Check that the system provide OA
# This is a one-time check, do not perform further checks if None is returned
If sum(flow_volumetric_air_outdoor) == 0
  return None
Endif

# This assumes that the system does provide OA to the space as per the first check
potential_failures_count = 0
potential_pass_count = 0
If number_occupants == 0
  If fraction_runtime_fan == 1
    return True
  Else
    return False
  Endif
Else
  If fraction_runtime_fan == 1 # the system could be "cycling" for the whole timestep so add to counter
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

- number_occupants: Number of occupants
  - Data Value Unit: count
  - Data Point Affiliation: Zone occupancy

- fraction_runtime_fan: Fan runtime fraction
  - Data Value Unit: fraction
  - Data Point Affiliation: System operation

- flow_volumetric_air_outdoor: Outdoor air flow rate
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: System ventilation

"""

from constrain.checklib import RuleCheckBase


class AppendixGHVACSystemFanOperation(RuleCheckBase):
    points = [
        "number_occupants",
        "fraction_runtime_fan",
        "flow_volumetric_air_outdoor",
    ]
    potential_failures_counter = 0
    potential_pass_count = 0

    def hvac_system_fan_operation(self, data):
        if data["number_occupants"] >= self.get_tolerance("ratio", "occupancy"):
            if data["fraction_runtime_fan"] == 1:
                return True
            else:
                return False
        else:
            # the system could be "cycling" for the whole timestep
            if data["fraction_runtime_fan"] == 1:
                self.potential_failures_counter += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool
            else:
                self.potential_pass_count += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool

    def check_system_oa(self, data):
        # check that the system does provide outdoor air
        total_oa = sum(data["flow_volumetric_air_outdoor"])
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
