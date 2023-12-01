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
else if oa_p < max_oa_p
    if abs(ra_p - max_ra_p) < ra_p_tol
        pass
    else
        fail
    end
else if abs(oa_p - max_oa_p) < oa_p_tol
    if ra_p < max_ra_p
        pass
    else
        fail
    end
end
```

"""

from constrain.checklib import RuleCheckBase


class G36ReturnAirDamperPositionForReliefDamperOrFan(RuleCheckBase):
    points = [
        "heating_output",
        "cooling_output",
        "ra_p",
        "max_ra_p",
        "ra_p_tol",
        "oa_p",
        "max_oa_p",
        "oa_p_tol",
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
        elif data["oa_p"] < data["max_oa_p"]:
            if abs(data["ra_p"] - data["max_ra_p"]) < data["ra_p_tol"]:
                return True
            else:
                return False
        elif abs(data["oa_p"] - data["max_oa_p"]) < data["oa_p_tol"]:
            if data["ra_p"] < data["max_ra_p"]:
                return True
            else:
                return False
        else:
            return "Untested"

    def verify(self):
        self.result = self.df.apply(lambda d: self.return_air_damper(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            if len(self.result[self.result == "Untested"] > 0):
                return "Untested"
            else:
                return True
