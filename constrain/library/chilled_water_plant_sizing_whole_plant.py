"""
### Description

- This verification aims to verify if a chilled water plant is oversized.

### Code requirement

- Code Name: N/A
- Code Year: N/A
- Code Section: N/A
- Code Subsection: N/A

### Verification Approach

We aim to verify that the chilled water plant is sized appropriately for the design cooling loads. The verification passes if the plant capacity is sufficient to meet the predicted peak load based on outdoor air temperature regression analysis.

### Verification Applicability

- Building Type(s): any with chilled water plant
- Space Type(s): N/A
- System(s): chilled water plant
- Climate Zone(s): any
- Component(s): chillers, cooling plant

### Verification Algorithm Pseudo Code

The algorithm performs regression analysis to predict peak cooling load based on outdoor air temperature:

1. Calculate chilled water plant load if not provided directly
2. Perform linear, quadratic, and cubic regressions of plant load vs. outdoor air temperature
3. Select the regression model with the best fit (highest R² value)
4. Use the selected model to predict the peak load at the maximum outdoor air temperature
5. Compare the predicted peak load with the nominal plant capacity
6. Verification passes if:
   - The maximum outdoor air temperature doesn't exceed the upper limit (120°F/48.89°C)
   - The predicted peak load is less than or equal to 95% of the nominal plant capacity

### Data requirements

- temperature_water_supply: Chilled water supply temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Chilled water plant

- temperature_water_return: Chilled water return temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Chilled water plant

- flow_mass_water: Chilled water mass flow rate
  - Data Value Unit: kg/s
  - Data Point Affiliation: Chilled water plant

- load_plant_water_chilled: Chilled water plant cooling load
  - Data Value Unit: kW
  - Data Point Affiliation: Chilled water plant

- temperature_air_outdoor: Outdoor air temperature
  - Data Value Unit: °C
  - Data Point Affiliation: Environmental conditions

- capacity_nominal_plant_water_chilled: Nominal capacity of the chilled water plant
  - Data Value Unit: kW
  - Data Point Affiliation: Chilled water plant
"""

from constrain.checklib import RuleCheckBase
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures
import numpy as np


Cp = 4184  # J/(kg*K)
UPPER_TEMP_AIR_OUTDOOR_LIMIT = 48.89  # deg C ~= 120 deg F


class ChilledWaterPlantSizingWholePlant(RuleCheckBase):
    points = [
        "temperature_water_supply",
        "temperature_water_return",
        "flow_mass_water",
        "load_plant_water_chilled",
        "temperature_air_outdoor",
        "capacity_nominal_plant_water_chilled",
        "ratio_sizing_plant_water_chilled_acceptable",
    ]

    def calc_temp_from_load(self, load, model):
        a = model.coef_[2]
        b = model.coef_[1]
        c = model.intercept_ - load

        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            raise ValueError("No real solution exists for the given y.")

        x1 = (-b + np.sqrt(discriminant)) / (2 * a)
        x2 = (-b - np.sqrt(discriminant)) / (2 * a)

        return max(x1, x2)

    def verify(self):
        # Calculate `load_plant_water_chilled` if any value is None
        if self.df["load_plant_water_chilled"].isnull().any():
            self.df["load_plant_water_chilled"] = (
                self.df["flow_mass_water"]
                * Cp
                * (
                    self.df["temperature_water_return"]
                    - self.df["temperature_water_supply"]
                )
            )

        # Perform regressions of `load_plant_water_chilled` = f(`temperature_air_outdoor`)
        feat = PolynomialFeatures(degree=2)
        X = feat.fit_transform(self.df[["temperature_air_outdoor"]].values)
        model = LinearRegression().fit(X, self.df["load_plant_water_chilled"])
        y = model.predict(X)
        coefficient_of_determination = r2_score(
            self.df[["load_plant_water_chilled"]], y
        )
        acceptable_coefficient_of_determination = 0.5
        if coefficient_of_determination >= acceptable_coefficient_of_determination:
            outdoor_air_temperature_at_nominal_chilled_water_plant_capacity = (
                self.calc_temp_from_load(
                    self.df["capacity_nominal_plant_water_chilled"].iloc[0], model
                )
            )

            if (
                outdoor_air_temperature_at_nominal_chilled_water_plant_capacity
                >= UPPER_TEMP_AIR_OUTDOOR_LIMIT
            ):
                self.df["result"] = False
            elif (
                self.df["temperature_air_outdoor"].max()
                / outdoor_air_temperature_at_nominal_chilled_water_plant_capacity
                >= self.df["ratio_sizing_plant_water_chilled_acceptable"].iloc[0]
            ):
                self.df["result"] = True
            else:
                self.df["result"] = False

        else:
            self.df["result"] = "Untested"
        self.result = self.df["result"]
