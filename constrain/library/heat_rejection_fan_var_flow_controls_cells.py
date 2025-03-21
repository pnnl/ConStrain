"""
### Description

This verification aims to check if multiple-cell heat rejection equipment properly stages its cells based on load. The system should maximize the number of active cells while maintaining minimum flow requirements for each cell.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2019
- Code Section: 6.5.5.2 Fan Control
- Code Subsection: Multiple-Cell Heat Rejection Equipment

### Verification Approach

The verification calculates the theoretical minimum number of cells needed:
1. Calculate required cells based on current flow rate and minimum flow per cell
2. Compare actual operating cells to theoretical minimum
3. Verify system isn't running fewer cells than theoretically required
   - This ensures maximum cell staging for efficient operation
   - Helps maintain minimum flow requirements per cell

### Verification Applicability

- Building Type(s): any
- Space Type(s): any
- System(s): multiple-cell cooling towers, fluid coolers
- Climate Zone(s): any
- Component(s): heat rejection fans, cell staging controls

### Verification Algorithm Pseudo Code

```python
# Calculate theoretical cells needed
theoretical_cells = (current_flow / design_flow * min_flow_per_cell / total_cells) + 0.9999
theoretical_cells = min(int(theoretical_cells), total_cells)

# Check if operating cells meet minimum requirement
if fan_power > 0:  # System is running
    if operating_cells < theoretical_cells:
        fail  # Too few cells operating
    else:
        pass  # Proper cell staging
```

### Data requirements

- ct_op_cells: Operating cells
  - Data Value Unit: count
  - Data point Description: Number of currently operating cells
  - Data Point Affiliation: System control

- ct_cells: Total cells
  - Data Value Unit: count
  - Data point Description: Total number of available cells
  - Data Point Affiliation: Equipment configuration

- ct_m: Current flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Current total system flow rate
  - Data Point Affiliation: System monitoring

- ct_P_fan: Fan power
  - Data Value Unit: watts
  - Data point Description: Current total fan power
  - Data Point Affiliation: System monitoring

- ct_m_des: Design flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Design total system flow rate
  - Data Point Affiliation: Equipment specifications

- min_flow_frac_per_cell: Minimum flow fraction
  - Data Value Unit: fraction
  - Data point Description: Minimum allowable flow per cell as fraction of design
  - Data Point Affiliation: Equipment specifications

"""

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
