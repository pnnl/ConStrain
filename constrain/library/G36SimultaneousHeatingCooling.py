"""
### Description

This verification aims to check if the system prevents simultaneous heating and cooling operation. The heating and cooling outputs should never be active at the same time to avoid energy waste and ensure proper system operation.

### Code requirement

- Code Name: ASHRAE Guideline 36
- Code Year: 2021
- Code Section: 5.16.2 Air Handling Unit Control Sequences
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
if heating_output > 0 and cooling_output > 0:
    fail  # Simultaneous heating and cooling detected
else:
    pass  # Normal operation
```

### Data requirements

- heating_output: Heating output
  - Data Value Unit: percent (0-100)
  - Data point Description: Current heating system output
  - Data Point Affiliation: System control

- cooling_output: Cooling output
  - Data Value Unit: percent (0-100)
  - Data point Description: Current cooling system output
  - Data Point Affiliation: System control

"""

from constrain.checklib import RuleCheckBase


class G36SimultaneousHeatingCooling(RuleCheckBase):
    points = ["heating_output", "cooling_output"]

    def simultaneous_heating_and_cooling(self, data):
        if data["heating_output"] > 0 and data["cooling_output"]:
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
