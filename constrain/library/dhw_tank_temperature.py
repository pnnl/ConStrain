from constrain.checklib import RuleCheckBase


class DHW_tank_temperature(RuleCheckBase):
    points = ["T_dhw", "T_dhw_deadband", "T_dhw_design_parameter"]

    def check_dhw_temperature(self, data):
        if (
            abs(data["T_dhw"] - data["T_dhw_design_parameter"])
            <= 0.5 * data["T_dhw_deadband"]
        ):
            return True
        else:
            return False

    def verify(self):
        self.result = self.df.apply(lambda d: self.check_dhw_temperature(d), axis=1)

    def check_bool(self):
        if len(self.result[self.result == False] > 0):
            return False
        else:
            return True
