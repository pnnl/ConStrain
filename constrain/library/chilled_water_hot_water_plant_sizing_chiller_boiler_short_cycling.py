"""
### Description

- Chillers/Boilers should be designed and controlled to prevent excessive cycling.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to identify the number of on/off transitions for each chiller/boiler in the system for each hour of operation. The verification passes if the number of transitions per hour does not exceed the maximum allowed cycles.

### Verification Applicability

- Building Type(s): any with chilled/hot water plant
- Space Type(s): N/A
- System(s): chilled/hot water plant
- Climate Zone(s): any
- Component(s): chillers/boilers

### Verification Algorithm Pseudo Code

The algorithm counts the number of status transitions (from on to off or off to on) for each hour

```python
# Normalize chiller/boiler status to 0s and 1s if needed
# For each hour, count the number of transitions between on and off states
# Compare the count with the maximum allowed cycles
if transitions_count <= cycles_number_maximum for all hours:
  return true
else:
  return false
end
```

### Data requirements

- status_equipment: Chiller/Boiler operation status
  - Data Value Unit: binary
  - Data Point Affiliation: Chiller/Boiler operation status

- cycles_number_maximum: Maximum allowed number of cycles per hour
  - Data Value Unit: count
  - Data Point Affiliation: Design specification

- system_type: System type (Chiller or Boiler)
  - Data Value Unit: N/A
  - Data Point Affiliation: N/A
"""

import pandas as pd

from constrain.checklib import RuleCheckBase


class ChilledWaterHotWaterPlantSizingChillerBoilerShortCycling(RuleCheckBase):
    points = [
        "status_equipment",
        "cycles_number_maximum",
        "system_type",
    ]

    def verify(self):
        # Normalize the status of the chiller/boiler
        self.df["status_equipment"] = self.df.apply(
            lambda x: 1 if x["status_equipment"] > 0 else 0, axis=1
        )

        # Identify transitions of operation
        transitions = self.df["status_equipment"].diff()

        # Initialization
        cycle_ends = []
        on_time = None
        # Iterate over the transitions to find cycles
        for i in range(1, len(transitions)):
            if transitions[i] == 1:  # Transition from 0 to 1 (chiller/boiler coming on)
                on_time = self.df.index[i]
            elif (
                transitions[i] == -1
            ):  # Transition from 1 to 0 (chiller/boiler coming off)
                if on_time is not None:
                    cycle_ends.append(self.df.index[i])
                    on_time = None

        # Create a Series for storing cycle end times
        cycles = pd.Series(1, index=pd.Index(cycle_ends))

        # Count number of cycles per rolling hour
        rolling_hour_cycles = cycles.rolling("1h").sum().fillna(0)
        rolling_hour_cycles = rolling_hour_cycles.to_frame(
            name="cycles_per_rolling_hour"
        )

        if (
            rolling_hour_cycles["cycles_per_rolling_hour"].max()
            > self.df["cycles_number_maximum"].iloc[0]
        ):
            self.df["result"] = False
        else:
            self.df["result"] = True

        self.result = self.df["result"]
