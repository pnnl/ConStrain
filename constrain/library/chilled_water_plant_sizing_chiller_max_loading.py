"""
### Description

- Verifies that chillers are properly sized by checking if the maximum loading ratio is reasonable.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to verify that chillers are properly sized by checking if the maximum loading ratio of the chiller exceeds the specified threshold during the simulation period. This ensures that chillers are not significantly oversized, which would lead to inefficient operation.

### Verification Applicability

- Building Type(s): any with chilled water plant
- Space Type(s): N/A
- System(s): chilled water plant
- Climate Zone(s): any
- Component(s): chillers

### Verification Algorithm Pseudo Code

The verification algorithm evaluates chiller sizing by analyzing the loading ratio throughout the simulation period:

```python
# Compare against the minimum acceptable maximum loading ratio (repeat for average loading ratio)
if ratio_loading_chiller_max > ratio_loading_chiller_max_min
  # Chiller is properly sized
  return true
else
  # Chiller is potentially oversized
  return false
end
```

### Data requirements

- ratio_loading_chiller: Chiller loading ratio over time
  - Data Value Unit: dimensionless (0-1)
  - Data Point Affiliation: chiller performance
  
- ratio_loading_chiller_max_min: Minimum acceptable maximum loading ratio
  - Data Value Unit: dimensionless (0-1)
  - Data Point Affiliation: design parameter

- ratio_loading_chiller_average_min: Minimum acceptable average loading ratio
  - Data Value Unit: dimensionless (0-1)
  - Data Point Affiliation: design parameter
"""

from constrain.checklib import RuleCheckBase


class ChilledWaterPlantSizingChillerMaxLoading(RuleCheckBase):
    points = [
        "ratio_loading_chiller",
        "ratio_loading_chiller_max_min",
        "ratio_loading_chiller_average_min",
    ]

    def verify(self):
        self.df["result"] = (
            max(self.df["ratio_loading_chiller"])
            >= self.df["ratio_loading_chiller_max_min"][0]
        ) & (
            (
                self.df["ratio_loading_chiller"].sum()
                / self.df["ratio_loading_chiller"].count()
            )
            >= self.df["ratio_loading_chiller_average_min"]
        )

        self.result = self.df["result"]
