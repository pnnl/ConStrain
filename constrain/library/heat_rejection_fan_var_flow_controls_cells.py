"""
### Description

Section 6.5.5.2.2
Multicell heat-rejection equipment with variable-speed fan drives shall
a. operate the maximum number of fans allowed that comply with the manufacturer’s requirements for all system components  
b. control all fans to the same fan speed required for the instantaneous cooling duty, as opposed to staged (on/off) operation. Minimum fan speed shall comply with the minimum
allowable speed of the fan drive system per the manufacturer’s recommendations.

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
theoretical_cells = (flow_mass_coolingtower / flow_mass_coolingtower_design * fraction_flow_min_cell / number_cells_coolingtower) + 0.9999
theoretical_cells = min(int(theoretical_cells), number_cells_coolingtower)

# Check if operating cells meet minimum requirement
if power_fan_coolingtower > 0:  # System is running
    if number_cells_coolingtower_operation < theoretical_cells:
        fail  # Too few cells operating
    else:
        pass  # Proper cell staging
```

### Data requirements

- number_cells_coolingtower_operation: Total number of cooling tower operating cells
  - Data Value Unit: count
  - Data Point Affiliation: System control

- number_cells_coolingtower: Total number of cooling tower cells
  - Data Value Unit: count
  - Data Point Affiliation: Equipment configuration

- flow_mass_coolingtower: Cooling tower mass flow
  - Data Value Unit: mass flow rate
  - Data Point Affiliation: System monitoring

- power_fan_coolingtower: Cooling tower fan power
  - Data Value Unit: power
  - Data Point Affiliation: Fan monitoring

- flow_mass_coolingtower_design: Cooling tower design mass flow
  - Data Value Unit: volumetric flow rate
  - Data Point Affiliation: Equipment specifications

- fraction_flow_min_cell: Minimum cooling tower cell flow fraction
  - Data Value Unit: fraction
  - Data Point Affiliation: Equipment specifications

"""

from constrain.checklib import RuleCheckBase


class HeatRejectionFanVariableFlowControlsCells(RuleCheckBase):
    points = [
        "number_cells_coolingtower_operation",
        "number_cells_coolingtower",
        "flow_mass_coolingtower",
        "power_fan_coolingtower",
        "flow_mass_coolingtower_design",
        "fraction_flow_min_cell",
    ]

    def verify(self):
        self.df["cells_op_theo_intermediate"] = (
            (self.df["flow_mass_coolingtower"])
            / self.df["flow_mass_coolingtower_design"]
            * self.df["fraction_flow_min_cell"]
            / self.df["number_cells_coolingtower_operation"]
        ) + 0.9999
        self.df["cells_op_theo_intermediate"] = self.df[
            "cells_op_theo_intermediate"
        ].astype("int")

        self.df["cells_op_theo"] = self.df[
            ["cells_op_theo_intermediate", "number_cells_coolingtower"]
        ].min(axis=1)

        self.result = ~(
            (self.df["number_cells_coolingtower_operation"] > 0)
            & (
                self.df["number_cells_coolingtower_operation"]
                < self.df["cells_op_theo"]
            )
            & (self.df["power_fan_coolingtower"] > self.get_tolerance("power", "fan"))
        )
