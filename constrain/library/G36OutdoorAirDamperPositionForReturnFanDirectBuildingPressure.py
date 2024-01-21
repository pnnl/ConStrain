"""
G36 2021

### Description

Section 5.16.2.3

### Verification Logic

```
if abs(oa_p - max_oa_p) < oa_p_tol
    pass
else
    fail
end
```

"""

from constrain.checklib import RuleCheckBase


class G36OutdoorAirDamperPositionForReturnFanDirectBuildingPressure(RuleCheckBase):
    points = [
        "oa_p",
        "max_oa_p",
        "oa_p_tol",
    ]

    def outdoor_air_damper(self, data):
        if abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.outdoor_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
