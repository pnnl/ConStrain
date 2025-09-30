"""
### Description

- This module contains functions to verify how often each individual chiller/boiler operates.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to verify that multiple chillers/boilers in a chilled/hot water plant are properly utilized. The verification passes if the chillers/boilers' operation time is at least 80% of the total plant operation time, indicating efficient use of multiple chillers/boilers.

### Verification Applicability

- Building Type(s): any with chilled/hot water plant
- Space Type(s): N/A
- System(s): chilled/hot water plant with multiple chillers/boilers
- Climate Zone(s): any
- Component(s): chillers/boilers

### Verification Algorithm Pseudo Code

The algorithm calculates the total operation time for chillers and the chilled/hot water plant:

1. Calculate the total operation time for chillers based on chiller status:
   ```
   For each timestep i:
     If status_equipment[i] > 0:
       duration_equipment[i] = timestep[i] - timestep[i-1]
     Else:
       duration_equipment[i] = 0
   
   equipment_load_hours = Sum(duration_equipment)
   ```

2. Calculate the total operation time for the chilled/hot water plant based on plant load:
   ```
   For each timestep i:
     If load_plant_water[i] > 0:
       duration_plant[i] = timestep[i] - timestep[i-1]
     Else:
       duration_plant[i] = 0
   
   plant_load_hours = Sum(duration_plant)
   ```

3. Calculate the ratio of chiller operation time to plant operation time:
   ```
   operation_ratio = equipment_load_hours / plant_load_hours
   ```

4. Verification passes if the ratio is greater than or equal to 0.8 (80%):
   ```
   result = operation_ratio >= 0.8
   ```

### Data requirements

- status_equipment: Chiller/Boiler operation status
  - Data Value Unit: binary
  - Data Point Affiliation: Chiller/Boiler operation schedule

- load_plant_water: Chilled/Hot water plant cooling/heating load
  - Data Value Unit: kW
  - Data Point Affiliation: Chilled/Hot water plant
"""

from constrain.checklib import RuleCheckBase

TOL_RATIO_GENERAL = 0.8


class ChilledWaterHotWaterPlantSizingMultipleChillersBoilers(RuleCheckBase):
    points = [
        "status_equipment",
        "load_plant_water",
    ]

    def get_runtimes(self, point, name):
        previous_time = 0
        self.df[name] = 0
        index = 0
        for (
            index,
            row,
        ) in self.df.iterrows():
            if row[point] > 0:
                if previous_time != 0:  # skip first record
                    self.df.loc[index, name] = (index - previous_time).total_seconds()
            previous_time = index

    def verify(self):
        self.get_runtimes("status_equipment", "equipment_runtime_seconds")
        self.get_runtimes("load_plant_water", "plant_runtime_seconds")
        self.df["result"] = (
            self.df["equipment_runtime_seconds"] / self.df["plant_runtime_seconds"]
        )
        self.result = self.df["result"]

    def check_bool(self):
        if self.df["equipment_runtime_seconds"].sum() / self.df[
            "plant_runtime_seconds"
        ].sum() >= (1 - self.get_tolerance("ratio", "general")):
            return True
        else:
            return False
