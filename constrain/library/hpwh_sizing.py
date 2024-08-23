from constrain.checklib import RuleCheckBase


class HPWH_sizing(RuleCheckBase):
    points = [
        "T_amb",
        "HeatingRate_dx_coil",
        "HeatingRate_waterheater1",
        "HeatingRate_waterheater2",
        "T_amb_parameter",
    ]

    def hpwh_load(self, data):
        total_hpwh_load = (
            data["HeatingRate_dx_coil"]
            + data["HeatingRate_waterheater1"]
            + data["HeatingRate_waterheater2"]
        )

        if data["T_amb"] <= data["T_amb_parameter"] or total_hpwh_load == 0.0:
            return "untested"
        elif data["HeatingRate_dx_coil"] / total_hpwh_load >= 1:
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.hpwh_load(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
