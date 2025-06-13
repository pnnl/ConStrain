"""
### Description

- Chillers should be designed and controlled to prevent excessive cycling.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to identify the number of on/off transitions for each chiller in the system for each hour of operation. The verification passes if the number of transitions per hour does not exceed the maximum allowed cycles.

### Verification Applicability

- Building Type(s): any with chilled water plant
- Space Type(s): N/A
- System(s): chilled water plant
- Climate Zone(s): any
- Component(s): chillers

### Verification Algorithm Pseudo Code

The algorithm counts the number of status transitions (from on to off or off to on) for each hour

```python
# Normalize chiller status to 0s and 1s if needed
# For each hour, count the number of transitions between on and off states
# Compare the count with the maximum allowed cycles
if transitions_count <= cycles_number_maximum for all hours:
  return true
else:
  return false
end
```

### Data requirements

- status_chiller: Chiller operation status
  - Data Value Unit: binary
  - Data Point Affiliation: Chiller operation status

- cycles_number_maximum: Maximum allowed number of on/off cycles per hour
  - Data Value Unit: count
  - Data Point Affiliation: Design specification
"""

from math import ceil

from constrain.checklib import RuleCheckBase


class ChilledWaterPlantSizingChillerShortCycling(RuleCheckBase):
    points = [
        "status_chiller",
        "cycles_number_maximum",
    ]

    def count_transitions(self, status_chiller):
        # Calculate the number of transitions between 1 and 0 for each hour

        return status_chiller.diff().abs().sum()

    def verify(self):

        # Normalize status_chiller to 0s and 1s if needed
        if not self.df["status_chiller"].isin([0, 1]).all():
            max_value = self.df["status_chiller"].max()
            if max_value > 0:  # Avoid division by zero
                self.df["status_chiller"] = (
                    self.df["status_chiller"] / max_value
                ).apply(ceil)

        # Extract hour from timestamp
        self.df["hour"] = self.df.index.hour

        transitions = (
            self.df.groupby("hour")["status_chiller"]
            .apply(self.count_transitions)
            .reset_index()
        )
        transitions = transitions.rename(
            columns={"status_chiller": "transitions_count"}
        )
        self.result = (
            transitions["transitions_count"] <= self.df["cycles_number_maximum"][0]
        )
