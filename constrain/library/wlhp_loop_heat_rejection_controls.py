from constrain.checklib import RuleCheckBase


class WLHPLoopHeatRejectionControl(RuleCheckBase):
    points = ["T_max_heating_loop", "T_min_cooling_loop", "m_pump"]

    def verify(self):
        self.df["T_max_heating_loop_max"] = (
            self.df.query(f"m_pump > {self.get_tolerance('waterflow', 'general')}")[
                "T_max_heating_loop"
            ]
        ).max()
        self.df["T_min_cooling_loop_min"] = (
            self.df.query(f"m_pump > {self.get_tolerance('waterflow', 'general')}")[
                "T_min_cooling_loop"
            ]
        ).min()
        self.result = (
            self.df["T_max_heating_loop_max"] - self.df["T_min_cooling_loop_min"]
        ) > (11.11 + self.get_tolerance("temperature", "general"))
