from constrain.checklib import RuleCheckBase


class AppendixGHVACSystemFanOperation(RuleCheckBase):
    points = ["o", "fan_runtime_fraction", "m_oa", "tol_o"]
    potential_failures_counter = 0
    potential_pass_count = 0

    def hvac_system_fan_operation(self, data):
        if data["o"] >= data["tol_o"]:
            if data["fan_runtime_fraction"] == 1:
                return True
            else:
                return False
        else:
            # the system could be "cycling" for the whole timestep
            if data["fan_runtime_fraction"] == 1:
                self.potential_failures_counter += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool
            else:
                self.potential_pass_count += 1
                return True  # assume that it passes, final failure/pass determination is handled by check_bool

    def check_system_oa(self, data):
        # check that the system does provide outdoor air
        total_oa = sum(data["m_oa"])
        if total_oa > 0:
            return True
        else:
            return False

    def check_bool(self) -> bool:
        if self.check_system_oa(self.df):
            if self.potential_failures_counter > 0 and self.potential_pass_count == 0:
                return False
            else:
                return True
        else:
            return None  # untested

    def verify(self):
        if self.check_system_oa(self.df):
            self.result = self.df.apply(
                lambda d: self.hvac_system_fan_operation(d), axis=1
            )
