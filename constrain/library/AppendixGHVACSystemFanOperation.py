"""
### Description

This verification aims to verify HVAC system fan operation as per ASHRAE 90.1 Appendix G rules. The system fan must run continuously during occupied periods and cycle on/off to meet heating and cooling loads during unoccupied hours.

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

- n_occupants: Number of occupants
  - Data Value Unit: count
  - Data point Description: Number of occupants
  - Data Point Affiliation: Zone occupancy

- frac_runtime_fan: Fan runtime fraction
  - Data Value Unit: fraction
  - Data point Description: Fan runtime fraction
  - Data Point Affiliation: System operation

- v_oa: Outdoor air flow rate
  - Data Value Unit: volumetric flow rate
  - Data point Description: Outdoor air flow rate
  - Data Point Affiliation: System ventilation

- tol_occupants: Occupancy threshold
  - Data Value Unit: count
  - Data point Description: Occupancy tolerance
  - Data Point Affiliation: Zone occupancy

"""

from constrain.checklib import RuleCheckBase


class AppendixGHVACSystemFanOperation(RuleCheckBase):
    points = ["n_occupants", "frac_runtime_fan", "v_oa", "tol_occupants"]
    potential_failures_counter = 0
    potential_pass_count = 0

    def hvac_system_fan_operation(self, data):
        if data["n_occupants"] >= data["tol_occupants"]:
            if data["frac_runtime_fan"] == 1:
                return True
            else:
                return False
        else:
            # the system could be "cycling" for the whole timestep
            if data["frac_runtime_fan"] == 1:
                self.potential_failures_counter += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool
            else:
                self.potential_pass_count += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool

    def check_system_oa(self, data):
        # check that the system does provide outdoor air
        total_oa = sum(data["v_oa"])
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
