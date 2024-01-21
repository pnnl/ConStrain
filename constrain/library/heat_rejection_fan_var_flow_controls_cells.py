from constrain.checklib import RuleCheckBase


class HeatRejectionFanVariableFlowControlsCells(RuleCheckBase):
    points = [
        "ct_op_cells",
        "ct_cells",
        "ct_m",
        "ct_P_fan",
        "ct_m_des",
        "min_flow_frac_per_cell",
    ]

    def verify(self):
        self.df["ct_cells_op_theo_intermediate"] = (
            self.df["ct_m"]
            / self.df["ct_m_des"]
            * self.df["min_flow_frac_per_cell"]
            / self.df["ct_cells"]
        ) + 0.9999
        self.df["ct_cells_op_theo_intermediate"] = self.df[
            "ct_cells_op_theo_intermediate"
        ].astype("int")

        self.df["ct_cells_op_theo"] = self.df[
            ["ct_cells_op_theo_intermediate", "ct_cells"]
        ].min(axis=1)

        self.result = ~(
            (self.df["ct_op_cells"] > 0)
            & (self.df["ct_op_cells"] < self.df["ct_cells_op_theo"])
            & (self.df["ct_P_fan"] > 0)
        )
