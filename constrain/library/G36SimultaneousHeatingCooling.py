"""
G36 2021

### Description

Section 5.16.2.3

### Verification logic

```
if heating_output > 0 and cooling_output > 0
    fail
else
    pass
end
``` 

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
