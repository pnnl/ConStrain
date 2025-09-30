"""
### Description

- This verification aims to verify if a hot water plant is oversized.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to verify that the hot water plant is sized appropriately for the design heating loads. The verification passes if the plant capacity is sufficient to meet the predicted peak load based on outdoor air temperature regression analysis.

### Verification Applicability

- Building Type(s): any with hot water plant
- Space Type(s): N/A
- System(s): hot water plant
- Climate Zone(s): any
- Component(s): boilers, heating plant

### Verification Algorithm Pseudo Code

```
if temperature_drybulb_day_design_heating is in dataset
    if peak_load >= nominal_hot_water_plant_capacity / oversizing_factor
        return True
    else
        return False
else
    return "Untested"
```

### Data requirements

- load_plant_water_hot: Hot water plant heating load
  - Data Value Unit: kW
  - Data Point Affiliation: Hot water plant

- temperature_air_outdoor: Outdoor air temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Environmental conditions

- capacity_nominal_plant_water_hot: Nominal capacity of the hot water plant
  - Data Value Unit: kW
  - Data Point Affiliation: Hot water plant

- temperature_drybulb_day_design_heating: Heating design day drybulb temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Design parameter

- factor_oversizing: Oversizing factor
  - Data Value Unit: fraction
  - Data Point Affiliation: Design parameter
"""

from constrain.checklib import RuleCheckBase


class HotWaterPlantSizingWholePlant(RuleCheckBase):
    points = [
        "load_plant_water_hot",
        "temperature_air_outdoor",
        "capacity_nominal_plant_water_hot",
        "temperature_drybulb_day_design_heating",
        "factor_oversizing",
    ]

    def verify(self):
        # Define analysis variables
        heating_design_day_outdoor_air_drybulb_temperature = self.df[
            "temperature_drybulb_day_design_heating"
        ].iloc[0]
        nominal_hot_water_plant_capacity = self.df[
            "capacity_nominal_plant_water_hot"
        ].iloc[0]
        oversizing_factor = self.df["factor_oversizing"].iloc[0]
        peak_load = self.df["load_plant_water_hot"].max()
        heating_design_day_outdoor_air_drybulb_temperature_range = self.df.loc[
            self.df["temperature_air_outdoor"]
            < heating_design_day_outdoor_air_drybulb_temperature
            + self.get_tolerance("temperature", "general"),
            "temperature_air_outdoor",
        ]

        # Check that the dataset covers a range of temperature close to the heating design dry-bulb temperature
        if len(heating_design_day_outdoor_air_drybulb_temperature_range) > 0:
            if peak_load >= nominal_hot_water_plant_capacity / oversizing_factor:
                self.df["result"] = True
            else:
                self.df["result"] = False
        else:
            self.df["result"] = "Untested"
        self.result = self.df["result"]
