import json
import logging
from collections import defaultdict

import brickschema
import yaml

DATAPOINTS_SOURCE = {
    "idf_output_variables": {},
    "parameters": {},
}


class BrickCompliance:
    def __init__(self, brick_schema: str, brick_instance: str) -> None:
        """Instantiate a BrickCompliance class object and load specified brick schema and brick instance.

        Args:
            brick_schema: str
                brick schema path (e.g., "../schema/Brick.ttl")
            brick_instance: str
                brick instance path (e.g., "../schema/brick_testing.ttl")
        """
        self.brick_schema = brick_schema
        self.brick_instance = brick_instance

        self.queried_datapoint_all_dict = defaultdict(list)

        self.verification_case_dict = {
            "no": "",
            "run_simulation": False,
            "simulation_IO": {
                "idf": "",
                "idd": "",
                "weather": "",
                "output": "",
                "ep_path": "",
            },
            "expected_result": "pass",
            "datapoints_source": {
                "idf_output_variables": {},
                "parameters": {},
            },
            "verification_class": "",
        }

        # Load brick schema and instance files
        self.g = brickschema.Graph(load_brick=True)
        self.g.load_file(self.brick_schema)
        self.g.expand(
            profile="rdfs"
        )  # reasoning on the graph, example: https://brickschema.org/tools/py-brickschema/
        self.g.parse(self.brick_instance, format="ttl")

        with open("./query_statement.yml", "r") as file:
            self.query_statement = yaml.safe_load(file)

        with open("./verification_datapoint_info.yml", "r") as file:
            self.verification_datapoint_info = yaml.safe_load(file)

    def validate_brick_instance(self):
        """Validate a brick instance against the brick schema."""

        valid, _, resultsText = self.g.validate()
        print(f"\nIs the brick instance valid?: {valid}\n{resultsText}")
        return valid, resultsText

    def get_applicable_verification_cases(self):
        """Get applicable verificaton cases with the given `brick_instance."""

        # TODO: 1) query all the classes/points 2) use the `get_applicable_library_items_by_datapoints` in the Verification Library class

        pass

    def query_verification_case_datapoints(
        self, verification_name: str, EnergyPlus_var_name: bool = True
    ) -> dict:
        """
        Query data point(s) for the given verification case.
        Args:
            verification_name: str
                verification item name(s) that will be queried

        Returns:
            self.queried_datapoint_all_dict: dict
                dictionary that includes verification item as a key and queried data point list as a value
        """

        query_result = self.g.query(self.query_statement[verification_name])

        # save the data point name in the instance
        for row in query_result:
            queried_datapoint_dict = {}
            for i in range(len(row)):
                queried_datapoint_dict[list(row.labels)[i]] = row[i].split("#")[1]

            self.queried_datapoint_all_dict[verification_name].append(
                queried_datapoint_dict
            )
        stop = 1

    def query_verification_cases_datapoints(self, verification_case_names: list = None):
        if verification_case_names is None:
            verification_case_names = []

        for verification_case_name in verification_case_names:
            self.query_verification_case_datapoints(verification_case_name)

    def query_with_customized_statement(
        self, query_statement: str, verification_name: str
    ):
        query_result = self.g.query(query_statement)
        stop = 1

        return True



    def serialize(
        self,
        instance_name: str = "new_library_verification_cases_from_brick_instance.json",
        EnergyPlus_var_name: bool = False,
    ) -> None:
        """
        Serialize the queried result.
        Args:
            lib_verification_cases_dict: dict
                dictionary in the format of ANIMATE input json format.

            instance_name: str
                serialized file name.
        """

        # Create input JSON format
        verification_cases_json = {"cases": []}

        for queried_data in self.queried_datapoint_all_dict["ZoneTempControl"]:
            for key, value in self.verification_datapoint_info["ZoneTempControl"][
                "default"
            ].items():
                self.verification_case_dict["datapoints_source"][
                    "idf_output_variables"
                ][key] = {}
                subject = queried_data[value[0]] if value[0] != "" else ""

                self.verification_case_dict["datapoints_source"][
                    "idf_output_variables"
                ][key].update(
                    {
                        "subject": subject,
                        "variable": queried_data[value[1]],
                        "frequency": "",
                    }
                )
            verification_cases_json["cases"].append(self.verification_case_dict)
        stop = 1
        # with open(f".{instance_name}", "w") as fw:
        #     json.dump(lib_verification_cases_dict, fw, indent=4)


if __name__ == "__main__":
    testing = BrickCompliance(
        brick_schema="./Brick.ttl",
        brick_instance="./brick_instance.ttl",
    )
    b = testing.validate_brick_instance()
    # e = testing.query_with_customized_statement(
    #     "SELECT ?cooling_setpoint ?heating_setpoint ?hvac_zone \n WHERE {\n ?hvac_zone a brick:HVAC_Zone . \n}",
    #     "ZoneTempControl",
    # )
    c = testing.query_verification_case_datapoints(
        "ZoneTempControl",
        #        "ZoneHeatSetpointMinimum",
        # "ZoneHeatingResetDepth",
        #        "ZoneCoolingSetpointMaximum",
        ##        "ZoneCoolingResetDepth",
        ##        "AutomaticShutdown",
        ##        "NightCycleOperation",  ## problem
        ##        "AutomaticOADamperControl",  ## problem
        ##        "VAVStaticPressureSensorLocation",  ## problem
        # "SupplyAirTempReset",
        ##        "EconomizerHighLimitA",
        ##        "EconomizerHighLimitB",
        ##        "EconomizerHighLimitC",
        ##        "EconomizerHighLimitD",
        ##        "IntegratedEconomizerControl",
        ##        "HWReset",
        ##        "CHWReset",
        ##        "WLHPLoopHeatRejectionControl",
        ##        "DemandControlVentilation",
        ##        "GuestRoomControlTemp",
        EnergyPlus_var_name=True,
    )
    d = testing.serialize(
        instance_name="new_library_verification_cases_from_brick_instance_True.json",
    )
