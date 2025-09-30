"""
### Description

- Verifies that chillers/boilers are properly sized by checking if the maximum loading ratio is reasonable.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to verify that chillers/boilers are properly sized by checking if the maximum loading ratio of the chiller/boiler exceeds the specified threshold during the simulation period. This ensures that chillers/boilers are not significantly oversized, which would lead to inefficient operation.

### Verification Applicability

- Building Type(s): any with chilled/hot water plant
- Space Type(s): N/A
- System(s): chilled/hot water plant
- Climate Zone(s): any
- Component(s): chillers/boilers

### Verification Algorithm Pseudo Code

The verification algorithm evaluates chiller/boiler sizing by analyzing the loading ratio throughout the simulation period:

```python
# Compare against the minimum acceptable maximum loading ratio (repeat for average loading ratio)
if ratio_loading_max > ratio_loading_max_min
  # Chiller/Boiler is properly sized
  return true
else
  # Chiller/Boiler is potentially oversized
  return false
end
```

### Data requirements

- ratio_loading: Chiller/Boiler loading ratio over time
  - Data Value Unit: dimensionless (0-1)
  - Data Point Affiliation: chiller/boiler performance
  
- ratio_loading_max_min: Minimum acceptable maximum loading ratio
  - Data Value Unit: dimensionless (0-1)
  - Data Point Affiliation: design parameter

- ratio_loading_average_min: Minimum acceptable average loading ratio
  - Data Value Unit: dimensionless (0-1)
  - Data Point Affiliation: design parameter

- system_type: System type (Chiller or Boiler)
  - Data Value Unit: N/A
  - Data Point Affiliation: N/A
"""

from constrain.checklib import RuleCheckBase


class ChilledWaterHotWaterPlantSizingChillerBoilerMaxLoading(RuleCheckBase):
    points = [
        "ratio_loading",
        "ratio_loading_max_min",
        "ratio_loading_average_min",
        "system_type",
    ]

    def verify(self):
        self.df["result"] = (
            max(self.df["ratio_loading"]) >= self.df["ratio_loading_max_min"][0]
        ) & (
            (self.df["ratio_loading"].sum() / self.df["ratio_loading"].count())
            >= self.df["ratio_loading_average_min"]
        )

        self.result = self.df["result"]
