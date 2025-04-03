"""
### Description

- This verification checks the set point tracking ability of local control loops.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A

### Verification Approach

The verification analyzes control error magnitude and frequency:
1. Calculate error threshold:
   - 5% of absolute setpoint value
   - Default 0.01 if setpoint is zero
2. For each sample, check if error exceeds threshold
3. Pass if less than 5% of samples have excessive error
   - Allows for occasional deviations
   - Ensures good tracking most of the time

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): any control loop
- Climate Zone(s): any
- Component(s): sensors, actuators, controllers

### Verification Algorithm Pseudo Code

```python
error_threshold = max(0.01, abs(value_setpoint) * 0.05)
excessive_error_count = 0
total_samples = 0

for each sample:
    error = abs(value_sensor - value_setpoint)
    if error > error_threshold:
        excessive_error_count += 1
    total_samples += 1

if excessive_error_count / total_samples > 0.05:
    fail  # Poor tracking performance
else:
    pass  # Acceptable tracking
```

### Data requirements

- value_sensor: Process variable
  - Data Value Unit: varies by application
  - Data Point Affiliation: Control loop input

- value_setpoint: Control setpoint
  - Data Value Unit: same as value_sensor
  - Data Point Affiliation: Control loop configuration

"""

from constrain.checklib import RuleCheckBase


class LocalLoopSetPointTracking(RuleCheckBase):
    points = ["value_sensor", "value_setpoint"]

    def error_below_5percent(self, t):
        # this method checks each sample, and returns true if the error is within 5 percent of absolute setpoint value
        # if the set point is 0, a default error threshold of 0.01 is used
        err_abs = abs(t["value_sensor"] - t["value_setpoint"])
        if t["value_setpoint"] == 0:
            if err_abs > 0.01:
                return False
            else:
                return True
        if err_abs / abs(t["value_setpoint"]) > 0.05:
            return False
        else:
            return True

    def verify(self):
        self.result = self.df.apply(lambda t: self.error_below_5percent(t), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False]) / len(self.result) > 0.05:
            return False
        else:
            return True
