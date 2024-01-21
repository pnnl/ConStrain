"""
G36 2021

### Description

Section 5.16.2.3

### Verification Logic

```
if heating_output > 0
    if abs(ra_p - max_ra_p) < ra_p_tol
        pass
    else
        fail
    end
else if cooling_output > 0
    if abs(ra_p - 0) < ra_p_tol
        pass
    else
        fail
    end
else 0 < ra_p < max_ra_p
    pass
else
    fail
end
```

"""
from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReturnFanDirectBuildingPressure(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "ra_p",
        "max_ra_p",
        "ra_p_tol",
    ]

    def return_air_damper(self, data):
        if data["heating_output"] > 0:
            if abs(data["ra_p"] - data["max_ra_p"]) < data["ra_p_tol"]:
                return True
            else:
                return False
        elif data["cooling_output"] > 0:
            if data["ra_p"] < data["ra_p_tol"]:
                return True
            else:
                return False
        elif 0 < data["ra_p"] < data["max_ra_p"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.return_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
