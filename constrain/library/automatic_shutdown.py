"""
### Description

Section 6.4.3.3.1 Automatic Shutdown
- Controls that can start and stop the system under different time schedules for seven different day types per week, are capable of retaining programming and time setting
during loss of power for a period of at least ten hours, and include an accessible manual override or equivalent function that allows temporary operation of the system for up to two hours.

### Code requirement

- Code Name: ASHRAE 90.1
- Code Year: 2016
- Code Section: 6.4.3 Controls and Diagnostics
- Code Subsection: 6.4.3.3.1 Off-hour automatic temperature setback and system shutoff with manual override

### Verification Approach

We aim to identify when the system comes on and when it is being turned off every day. The verification passes if we observed different start and end time for the whole simulation period.

### Verification Applicability

- Building Type(s): any
- Space Type(s): N/A
- System(s): any
- Climate Zone(s): any
- Component(s): air loops and fans

### Verification Algorithm Pseudo Code

The first step is to create data that represents the difference in system status (using `status_hvac`) from timesteps to the previous ones. This can be done by using `pandas.DataFrame.diff`. Then, we need to filter out all values equal to 0 which represent to change in system status (meaning that the system is still off or still on when compared with the previous timestep). Finally, we need retrieve the first and last value for each day, see [here](https://stackoverflow.com/questions/52909610/pandas-getting-first-and-last-value-from-each-day-in-a-datetime-dataframe) for an example, and store the data in a dataframe with two columns: `start_time` and `end_time`. Once this is done, proceed with the following evaluation:

```python
if min(start_time) != max(start_time) and min(end_time) != max(end_time)
  return true
else
  return false
end
```

### Data requirements

-  status_hvac: HVAC operation status
  - Data Value Unit: binary
  - Data Point Affiliation: HVAC operation schedule

"""

import pandas as pd
from constrain.checklib import RuleCheckBase


class AutomaticShutdown(RuleCheckBase):
    points = ["status_hvac"]

    def verify(self):
        copied_df = (
            self.df.copy()
        )  # copied not to store unnecessary intermediate variables in self.df dataframe
        copied_df.index.name = "Date"  # rename the index column to Date
        copied_df.reset_index(
            inplace=True
        )  # convert index column back to normal column
        copied_df["hvac_operation_diff"] = copied_df[
            "status_hvac"
        ].diff()  # calculate the difference between previous and current rows
        copied_df = copied_df.dropna(axis=0)  # drop NaN row
        copied_df = copied_df.loc[
            copied_df["hvac_operation_diff"] != 0.0
        ]  # filter out 0.0 values
        copied_df["Date"] = pd.to_datetime(
            copied_df["Date"], format="%Y-%m-%d %H:%M:%S"
        )
        df2 = copied_df.groupby(pd.to_datetime(copied_df["Date"]).dt.date).apply(
            lambda x: x.iloc[[0, -1]]
        )  # group by start/end time

        # Get min/max start/end times
        min_start_time = df2.query("hvac_operation_diff == 1")["Date"].dt.hour.min()
        max_start_time = df2.query("hvac_operation_diff == 1")["Date"].dt.hour.max()
        min_end_time = df2.query("hvac_operation_diff == -1")["Date"].dt.hour.min()
        max_end_time = df2.query("hvac_operation_diff == -1")["Date"].dt.hour.max()

        check = (min_start_time != max_start_time) & (min_end_time != max_end_time)

        self.df["result"] = check
        self.result = self.df["result"]
