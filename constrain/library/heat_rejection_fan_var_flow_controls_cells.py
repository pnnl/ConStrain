"""
### Description

This verification aims to check if multiple-cell heat rejection equipment properly stages its cells based on load. The system should maximize the number of active cells while maintaining minimum flow requirements for each cell.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.5.5.2 Fan Speed Control
- Code Subsection: 6.5.5.2.2

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

- n_cells_ct_ct_op: Operating cells
  - Data Value Unit: count
  - Data point Description: Number of operating cooling tower cells
  - Data Point Affiliation: System control

- n_cells_ct: Total cells
  - Data Value Unit: count
  - Data point Description: Number of cooling tower cells
  - Data Point Affiliation: Equipment configuration

- m_ct: Current flow
  - Data Value Unit: mass flow rate
  - Data point Description: Cooling tower mass flow rate
  - Data Point Affiliation: System monitoring

- p_power_fan_ct: Fan power
  - Data Value Unit: power
  - Data point Description: Cooling tower fan power
  - Data Point Affiliation: Fan monitoring

- m_ct_design: Design flow
  - Data Value Unit: volumetric flow rate
  - Data point Description: Cooling tower design flow rate
  - Data Point Affiliation: Equipment specifications

- ratio_v_cell_min: Minimum flow fraction
  - Data Value Unit: fraction
  - Data point Description: Minimum cell flow ratio
  - Data Point Affiliation: Equipment specifications

"""

from constrain.checklib import RuleCheckBase


class HeatRejectionFanVariableFlowControlsCells(RuleCheckBase):
    points = [
        "n_cells_ct_ct_op",
        "number_cells_coolingtower",
        "flow_mass_coolingtower",
        "power_fan_coolingtower",
        "flow_mass_coolingtower_design",
        "ratio_v_cell_min",
    ]

    def verify(self):
        self.df["cells_op_theo_intermediate"] = (
            self.df["flow_mass_coolingtower"]
            / self.df["flow_mass_coolingtower_design"]
            * self.df["ratio_v_cell_min"]
            / self.df["number_cells_coolingtower"]
        ) + 0.9999
        self.df["cells_op_theo_intermediate"] = self.df[
            "cells_op_theo_intermediate"
        ].astype("int")

        self.df["cells_op_theo"] = self.df[
            ["cells_op_theo_intermediate", "number_cells_coolingtower"]
        ].min(axis=1)

        self.result = ~(
            (self.df["n_cells_ct_ct_op"] > 0)
            & (self.df["n_cells_ct_ct_op"] < self.df["cells_op_theo"])
            & (self.df["power_fan_coolingtower"] > 0)
        )
