"""
### Description

- This module contains functions to verify how often each individual chiller operates.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to verify that multiple chillers in a chilled water plant are properly utilized. The verification passes if the chillers' operation time is at least 80% of the total plant operation time, indicating efficient use of multiple chillers.

### Verification Applicability

- Building Type(s): any with chilled water plant
- Space Type(s): N/A
- System(s): chilled water plant with multiple chillers
- Climate Zone(s): any
- Component(s): chillers

### Verification Algorithm Pseudo Code

The algorithm calculates the total operation time for chillers and the chilled water plant:

1. Calculate the total operation time for chillers based on chiller status:
   ```
   For each timestep i:
     If status_chiller[i] > 0:
       duration_chiller[i] = timestep[i] - timestep[i-1]
     Else:
       duration_chiller[i] = 0
   
   chiller_load_hours = Sum(duration_chiller)
   ```

2. Calculate the total operation time for the chilled water plant based on plant load:
   ```
   For each timestep i:
     If load_plant_water_chilled[i] > 0:
       duration_plant[i] = timestep[i] - timestep[i-1]
     Else:
       duration_plant[i] = 0
   
   plant_load_hours = Sum(duration_plant)
   ```

3. Calculate the ratio of chiller operation time to plant operation time:
   ```
   operation_ratio = chiller_load_hours / plant_load_hours
   ```

4. Verification passes if the ratio is greater than or equal to 0.8 (80%):
   ```
   result = operation_ratio >= 0.8
   ```

### Data requirements

- status_chiller: Chiller operation status
  - Data Value Unit: binary
  - Data Point Affiliation: Chiller operation schedule

- load_plant_water_chilled: Chilled water plant cooling load
  - Data Value Unit: kW
  - Data Point Affiliation: Chilled water plant
"""

from datetime import timedelta

from constrain.checklib import RuleCheckBase

TOL_RATIO_GENERAL = 0.8


class ChilledWaterPlantSizingMultipleChillers(RuleCheckBase):
    points = [
        "status_chiller",
        "load_plant_water_chilled",
    ]

    def time_calculation(self, df):
        # Initializing duration columns to zero timedelta
        df["duration_chiller"] = timedelta(0)
        df["duration_plant_water_chilled"] = timedelta(0)

        last_operation = df.index[0]

        # Utilize iterrows if operation needs DataFrame-level modification
        for i in df.index:
            index_diff = i - last_operation

            if df.at[i, "status_chiller"] > 0.0:
                df.at[i, "duration_chiller"] = index_diff

            if df.at[i, "load_plant_water_chilled"] > 0.0:
                df.at[i, "duration_plant_water_chilled"] = index_diff

            last_operation = i

        # Sum durations
        load_hours_chiller = df["duration_chiller"].sum()
        load_hours_plant_water_chilled = df["duration_plant_water_chilled"].sum()

        return load_hours_chiller, load_hours_plant_water_chilled

    def verify(self):

        # Calculate total load hours
        chiller_load_hours, plant_water_chilled_load_hours = self.time_calculation(
            self.df
        )

        # Store the boolean result in the result column
        self.df["result"] = (
            chiller_load_hours / plant_water_chilled_load_hours >= TOL_RATIO_GENERAL
        )

        # Save result in instance variable
        self.result = self.df["result"]
