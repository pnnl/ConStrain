"""
### Description

Section 5.16.2.3
- Supply air temperature shall be controlled to setpoint using a control loop whose output is mapped to sequence the heating coil (if applicable), outdoor air damper, return air damper, and cooling coil

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Supply Air Temperature Control
- Code Subsection: 5.16.2.3 Prevention of Simultaneous Heating and Cooling

### Verification Approach

The verification monitors heating and cooling outputs to ensure they are not active simultaneously. If both outputs show non-zero values at any time, this indicates improper control that wastes energy through simultaneous heating and cooling.

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): Any HVAC system with both heating and cooling capability
- Climate Zone(s): any
- Component(s): heating coils, cooling coils, control sequences

### Verification Algorithm Pseudo Code

```python
if output_coil_heating > 0 and output_coil_cooling > 0:
    fail  # Simultaneous heating and cooling detected
else:
    pass  # Normal operation
```

### Data requirements

- output_coil_heating: Heating signal
  - Data Value Unit: percent
  - Data Point Affiliation: System control

- output_coil_cooling: Cooling signal
  - Data Value Unit: percent
  - Data Point Affiliation: System control

"""

from constrain.checklib import RuleCheckBase


class G36SimultaneousHeatingCooling(RuleCheckBase):
    points = ["output_coil_heating", "output_coil_cooling"]

    def simultaneous_heating_and_cooling(self, data):
        if data["output_coil_heating"] > self.get_tolerance("load", "coil") and data[
            "output_coil_cooling"
        ] > self.get_tolerance("load", "coil"):
            return False
        else:
            return True

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.simultaneous_heating_and_cooling(d), axis=1
        )

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
