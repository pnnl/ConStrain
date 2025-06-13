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


Cp = 4.184  # kJ/(kg*K), specific heat
UPPER_TEMP_AIR_OUTDOOR_LIMIT = 48.89  # deg C ~= 120 deg F
ACCEPTABLE_CHILLER_SIZING_RATIO = 0.95


class ChilledWaterPlantSizingWholePlant(RuleCheckBase):
    points = [
        "temperature_water_supply",
        "temperature_water_return",
        "flow_mass_water",
        "load_plant_water_chilled",
        "temperature_air_outdoor",
        "capacity_nominal_plant_water_chilled",
    ]

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

        # Perform linear, quadratic, cubic  regressions of `load_plant_water_chilled` = f(`temperature_air_outdoor`)
        # 1. linear
        linear_model = LinearRegression().fit(
            self.df[["temperature_air_outdoor"]], self.df[["load_plant_water_chilled"]]
        )

        # 1.1 Make a prediction
        y_pred_linear = linear_model.predict(self.df[["temperature_air_outdoor"]])

        # 1.2 Calculate R^2 value
        r_squared_linear = r2_score(
            self.df[["load_plant_water_chilled"]], y_pred_linear
        )

        # 2. quadratic
        # 2.1 Transform features to quadratic (second-degree)
        quadratic_feature = PolynomialFeatures(degree=2)
        x_quadratic = quadratic_feature.fit_transform(
            self.df[["temperature_air_outdoor"]]
        )

        # 2.2 train the model
        quadratic_model = LinearRegression().fit(
            x_quadratic, self.df[["load_plant_water_chilled"]]
        )

        # 2.3 Make a prediction
        y_quadratic_pred = quadratic_model.predict(x_quadratic)

        # 2.4 Calculate R^2 value
        r_squared_quadratic = r2_score(
            self.df[["load_plant_water_chilled"]], y_quadratic_pred
        )

        # 3. cubic
        # 3.1 Transform features to quadratic (third-degree)
        cubic_feature = PolynomialFeatures(degree=3)
        x_cubic = cubic_feature.fit_transform(self.df[["temperature_air_outdoor"]])

        # 3.2 train the model
        cubic_model = LinearRegression().fit(
            x_cubic, self.df[["load_plant_water_chilled"]]
        )

        # 3.3 Make a prediction
        y_cubic_pred = cubic_model.predict(x_cubic)

        # 3.4 Calculate R^2 value
        r_squared_cubic = r2_score(self.df[["load_plant_water_chilled"]], y_cubic_pred)

        # select regression model based on R^2 value
        # if the R2 value is the same, use the lower-degree model
        max_r_squared = max(r_squared_linear, r_squared_quadratic, r_squared_cubic)
        if r_squared_linear == r_squared_linear:
            model = linear_model
            pred_value = [[self.df["temperature_air_outdoor"].max()]]
        elif r_squared_quadratic == r_squared_linear:
            model = quadratic_model
            pred_value = quadratic_feature.fit_transform(
                [[self.df["temperature_air_outdoor"].max()]]
            )
        else:
            model = cubic_model
            pred_value = cubic_feature.fit_transform(
                [[self.df["temperature_air_outdoor"].max()]]
            )

        # Verification
        if (self.df["temperature_air_outdoor"] > UPPER_TEMP_AIR_OUTDOOR_LIMIT).any():
            self.df["result"] = False
        elif (
            model.predict(pred_value)
            / self.df["capacity_nominal_plant_water_chilled"][0]
            >= ACCEPTABLE_CHILLER_SIZING_RATIO
        ):
            self.df["result"] = True
        else:
            self.df["result"] = False

        self.result = self.df["result"]
