from constrain.checklib import RuleCheckBase


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = ["T_max_heating_loop", "T_min_cooling_loop", "m_pump"]

    def verify(self):
        # Get max heating loop temp when pump is running
        self.df["T_max_heating_loop_max"] = (
            self.df.query("m_pump > 0.01")[
                "T_max_heating_loop"
            ]  # Pump effectively running (>1%)
        ).max()

        # Get min cooling loop temp when pump is running
        self.df["T_min_cooling_loop_min"] = (
            self.df.query("m_pump > 0.01")[
                "T_min_cooling_loop"
            ]  # Pump effectively running (>1%)
        ).min()

        # Check if temperature difference meets requirement with tolerance
        self.result = (
            self.df["T_max_heating_loop_max"] - self.df["T_min_cooling_loop_min"]
        ) > (
            11.11 - self.get_tolerance("temperature", "general")
        )  # 11.11°C = 20°F
