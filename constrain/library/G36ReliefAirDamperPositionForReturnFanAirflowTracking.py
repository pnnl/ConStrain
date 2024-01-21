"""
G36 2021

### Description

Section 5.16.2.3

### Verification Logic

```
if heating_output > 0
    if abs(rea_p - 0) < rea_p_tol
        pass
    else
        fail
    end
else if cooling_output > 0
    if abs(rea_p - max_rea_p) < rea_p_tol
        pass
    else
        fail
    end
else if abs(rea_p - (1 - ra_p) * max_rea_p) < rea_p_tol
    pass
else
    fail
end
```

"""

from constrain.checklib import RuleCheckBase


class G36ReliefAirDamperPositionForReturnFanAirflowTracking(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "rea_p",
        "max_rea_p",
        "rea_p_tol",
        "ra_p",
    ]

    def relief_air_damper(self, data):
        if data["heating_output"] > 0:
            if data["rea_p"] < data["rea_p_tol"]:
                return True
            else:
                return False
        elif data["cooling_output"] > 0:
            if abs(data["rea_p"] - data["max_rea_p"]) < data["rea_p_tol"]:
                return True
            else:
                return False
        elif (
            abs(data["rea_p"] - (1 - data["ra_p"]) * data["max_rea_p"])
            < data["rea_p_tol"]
        ):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.relief_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
