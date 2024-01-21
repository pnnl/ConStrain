"""
G36 2021

### Description

Section 5.16.2.3

### Verification logic

```
if t_max > max_clg_sa_t_sp
    fail
end

switch operation_mode
case "cooldown"
    sa_t_sp = min_clg_sa_t_sp
case "warmup", "setback
    sa_t_sp = 95 # F
case "occupied", "setup"
    if oa_t <= oa_t_min
        sa_t_sp = t_max
    else if oa_t >= oa_t_max
        sa_t_sp = min_clg_sa_t_sp
    else
        sa_t_sp = (oa_t - oa_t_min) * (t_max - min_clg_sa_t_sp) / (oa_t_min - oa_t_max) + t_max # linear interpolation
    end
end

if abs(sa_t_sp - sa_t_sp_ac) < sa_sp_tol
    pass
else
    fail
end
``` 

"""
from constrain.checklib import RuleCheckBase
import numpy as np


class G36SupplyAirTemperatureSetpoint(RuleCheckBase):
    points = [
        "operation_mode",
        "t_max",
        "max_clg_sa_t_sp",
        "min_clg_sa_t_sp",
        "oa_t",
        "oa_t_min",
        "oa_t_max",
        "sa_t_sp_ac",
        "sa_sp_tol",
    ]

    def supply_air_temperature_setpoint(self, data):
        if data["t_max"] > data["max_clg_sa_t_sp"]:
            return False
        sa_t_sp = -999
        if data["operation_mode"] == "cooldown":
            sa_t_sp = data["min_clg_sa_t_sp"]
        elif data["operation_mode"] in ["warmup", "setback"]:
            sa_t_sp = 35.0  # 95 deg. F
        elif data["operation_mode"] in ["occupied", "setup"]:
            if data["oa_t"] <= data["oa_t_min"]:
                sa_t_sp = data["t_max"]
            elif data["oa_t"] >= data["oa_t_max"]:
                sa_t_sp = data["min_clg_sa_t_sp"]
            else:
                sa_t_sp = (data["oa_t"] - data["oa_t_min"]) * (
                    data["t_max"] - data["min_clg_sa_t_sp"]
                ) / (data["oa_t_min"] - data["oa_t_max"]) + data["t_max"]
        if sa_t_sp == -999:
            return np.nan
        if abs(sa_t_sp - data["sa_t_sp_ac"]) < data["sa_sp_tol"]:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(
            lambda d: self.supply_air_temperature_setpoint(d), axis=1
        )
