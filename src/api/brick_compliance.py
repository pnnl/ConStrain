import copy
import json
import logging
from collections import defaultdict

import brickschema
import yaml


class BrickCompliance:
    def __init__(
        self,
        brick_schema_path: str,
        brick_instance_path: str,
        query_statement_path: str = "./resources/brick/query_statement.yml",
        datapoint_name_conversion_path: str = "./resources/brick/verification_datapoint_info.yml",
        perform_reasoning: bool = False,
    ) -> None:
        """Instantiate a BrickCompliance class object and load specified brick schema and brick instance.

        Args:
            brick_schema_path: str
                brick schema path (e.g., "../schema/Brick.ttl")
            brick_instance_path: str
                brick instance path (e.g., "../schema/brick_testing.ttl")
            query_statement_path: `str`
                the query statements file path. The default path is `./resources/brick/query_statement.yml`.
            datapoint_name_conversion_path: str
                the datapoint conversion name saving yaml file. The default path is `./resources/brick/verification_datapoint_info.yml`.
            perform_reasoning: `bool` argument whether reasoning is performed to the given instance. The default boolean value is False.

        """
        # check arg types
        if not isinstance(brick_schema_path, str):
            logging.error(
                f"The `brick_schema_path` argument type must be str, but {type(brick_schema_path)} type is provided."
            )
            return None

        if not isinstance(brick_instance_path, str):
            logging.error(
                f"The `brick_instance_path` argument type must be str, but {type(brick_instance_path)} type is provided."
            )
            return None

        if not isinstance(datapoint_name_conversion_path, str):
            logging.error(
                f"The `datapoint_name_conversion_path` argument type must be str, but {type(datapoint_name_conversion_path)} type is provided."
            )
            return None

        if not isinstance(perform_reasoning, bool):
            logging.error(
                f"The `perform_reasoning` argument type must be bool, but {type(perform_reasoning)} type is provided."
            )
            return None

        # define variables
        self.brick_schema_path = brick_schema_path
        self.brick_instance_path = brick_instance_path

        self.queried_datapoint_all_dict = defaultdict(list)

        self.verification_case_dict = {
            "datapoints_source": {
                "idf_output_variables": {},
            },
            "verification_class": "",
        }

        # load brick schema and instance files
        self.g = brickschema.Graph(load_brick=True)
        self.g.load_file(self.brick_schema_path)
        if perform_reasoning:
            self.g.expand(
                profile="rdfs"
            )  # reasoning on the graph, example: https://brickschema.org/tools/py-brickschema/
        self.g.parse(self.brick_instance_path, format="ttl")

        # load files needed for brick
        try:
            with open(query_statement_path, "r") as file:
                self.query_statement = yaml.safe_load(file)
        except FileNotFoundError:
            logging.error(
                f"The query statement file isn't found. Please verify the {self.query_statement} path."
            )
            return None

        try:
            with open(datapoint_name_conversion_path, "r") as file:
                self.verification_datapoint_info = yaml.safe_load(file)
        except FileNotFoundError:
            logging.error(
                f"The datapoint name conversion file isn't found. Please verify the {datapoint_name_conversion_path} path."
            )
            return None

        try:
            with open("./schema/library.json", "r") as file:
                self.library_json = json.load(file)
        except FileNotFoundError:
            logging.error(
                f"The library json file isn't found. Please verify that the file exists in the `schema` folder."
            )
            return None

    def validate_brick_instance_path(self):
        """Validate a brick instance against the brick schema.

        Returns:
            valid: bool
                whether the validation passes/fails

            resultsText: str
                Message from the validation process

        """

        valid, _, resultsText = self.g.validate()
        print(f"\nIs the brick instance valid?: {valid}\n{resultsText}")

        return valid, resultsText

    def get_applicable_verification_lib_items(
        self,
        verification_lib_item_list: list = None,
    ):
        """Get applicable control verification library items among the `verification_item_lib_name` list from the brick instance.

        Args:
            verification_item_lib_name: list
                list of verification item names. If empty list is provided, all the available verification library items are used.

        Returns: list
            list that includes available verification library item names from the given brick instance.

        """

        # check arg types
        if verification_lib_item_list is None:
            verification_lib_item_list = []
        elif not isinstance(verification_lib_item_list, list):
            # raise an error
            pass

        # determine total verification lib items to iterate. If `verification_lib_item_list` is empty, all the available verification items are used
        if verification_lib_item_list:
            verification_lib_items = verification_lib_item_list
        else:
            verification_lib_items = list(self.query_statement)

        # find if queried datapoints are the same as verification lib item
        # TODO: This logic doesn't work with the verification lib item that has parameter(s). Fix the logic.
        available_verification_item_list = []
        for verification_lib_item in verification_lib_items:
            for query_result in self.query_verification_case_datapoints(
                verification_lib_item
            ):
                if set(
                    query_result["datapoints_source"]["idf_output_variables"]
                ) == set(
                    self.library_json[verification_lib_item]["description_datapoints"]
                ):
                    available_verification_item_list.append(verification_lib_item)

        return list(set(available_verification_item_list))

    def query_verification_case_datapoints(
        self, verification_item_lib_name: str, energyplus_naming_assembly: bool = True
    ) -> list:
        """
        Query data point(s) for the given verification case.

        Args:
            verification_item_lib_name: str
                verification item name(s) that will be queried

        Returns:
            self.queried_datapoint_all_dict: dict
                dictionary that includes verification item as a key and queried data point list as a value
        """

        # check arg types
        if not isinstance(verification_item_lib_name, str):
            logging.error(
                f"The `verification_item_lib_name` argument type must be str, but {type(verification_item_lib_name)} type is provided."
            )
            return None

        if not isinstance(energyplus_naming_assembly, bool):
            logging.error(
                f"The `energyplus_naming_assembly` argument type must be bool, but {type(energyplus_naming_assembly)} type is provided."
            )
            return None

        # perform query
        query_result = self.g.query(self.query_statement[verification_item_lib_name])

        # organize query result
        quried_verification_datapoints = self._organize_query_results(
            query_result, verification_item_lib_name, energyplus_naming_assembly
        )

        return quried_verification_datapoints

    def query_with_customized_statement(
        self,
        custom_query_statement: str,
        verification_item_lib_name: str,
        energyplus_naming_assembly: bool = True,
    ) -> list:
        """Query datapoints with a customized query statement. When implemented, the quality check of the `query_statement` is done by checking whether the number of queried variables are the same as the required number of data points in the verification library item.

        Args:
            custom_query_statement: str
                query statement written from users

            verification_item_lib_name: str
                verification library item of the query_statement

            energyplus_naming_assembly: bool
                whether to convert the queried datapoints' name to EnergyPlus style variable name.

        Returns:
            queried result in the verification case format. `str` message from the `query_statement`'s quality check result.

        """
        # check arg types
        if not isinstance(custom_query_statement, str):
            logging.error(
                f"The `custom_query_statement` argument type must be str, but {type(custom_query_statement)} type is provided."
            )
            return None

        if not isinstance(verification_item_lib_name, bool):
            logging.error(
                f"The `verification_item_lib_name` argument type must be str, but {type(verification_item_lib_name)} type is provided."
            )
            return None

        if not isinstance(energyplus_naming_assembly, bool):
            logging.error(
                f"The `energyplus_naming_assembly` argument type must be bool, but {type(energyplus_naming_assembly)} type is provided."
            )
            return None

        # perform query
        query_result = self.g.query(custom_query_statement)

        # organize query result
        quried_verification_datapoints = self._organize_query_results(
            query_result, verification_item_lib_name, energyplus_naming_assembly
        )

        # quality check - whether the no. of queried variables == required no. of data points in the verification library item
        total_no_of_datapoints = len(
            self.library_json[verification_item_lib_name]["description_datapoints"]
        )

        for queried_datapoints in self.queried_datapoint_all_dict[
            verification_item_lib_name
        ]:
            if "hvac_zone" in queried_datapoints:
                if len(queried_datapoints) != total_no_of_datapoints + 1:
                    logging.error(
                        f"The number of datapoints with the customized query statement is {len(queried_datapoints)-1} and the number of required datapoints for {verification_item_lib_name} verification item is {total_no_of_datapoints}. The two numbers must be the same."
                    )
                    return None
            else:
                if len(queried_datapoints) != total_no_of_datapoints:
                    logging.error(
                        f"The number of datapoints with the customized query statement is {len(queried_datapoints)} and the number of required datapoints for {verification_item_lib_name} verification item is {total_no_of_datapoints}. The two numbers must be the same."
                    )
                    return None

        return quried_verification_datapoints

    def _organize_query_results(
        self,
        query_result,
        verification_item_lib_name: str,
        energyplus_naming_assembly: bool,
    ):

        # save the data point name in the instance
        for row in query_result:
            queried_datapoint_dict = {}
            for i in range(len(row)):
                queried_datapoint_dict[list(row.labels)[i]] = row[i].split("#")[1]

            self.queried_datapoint_all_dict[verification_item_lib_name].append(
                queried_datapoint_dict
            )

        # convert to the verification case format
        result = self._convert_to_verification_case_format_helper(
            verification_item_lib_name, energyplus_naming_assembly
        )

        return result

    def _convert_to_verification_case_format_helper(
        self, verification_case_name: str, energyplus_naming_assembly: str
    ) -> list:

        verification_case_saving_list = []

        for idx, query_dict in enumerate(
            self.queried_datapoint_all_dict[verification_case_name]
        ):
            verification_case_dict_copy = copy.deepcopy(self.verification_case_dict)
            verification_case_dict_copy["verification_class"] = verification_case_name

            conversion_setting = (
                "EnergyPlus" if energyplus_naming_assembly else "default"
            )
            datapoint_info = self.verification_datapoint_info[verification_case_name][
                conversion_setting
            ]

            for key, value in query_dict.items():
                if key not in ("hvac_zone"):
                    point_nonmen = self.verification_datapoint_info[
                        verification_case_name
                    ][conversion_setting][key]["point"]
                    verification_case_dict_copy["datapoints_source"][
                        "idf_output_variables"
                    ][point_nonmen] = {}

                    if energyplus_naming_assembly:
                        verification_case_dict_copy["datapoints_source"][
                            "idf_output_variables"
                        ][point_nonmen].update(
                            {
                                "subject": self.queried_datapoint_all_dict[
                                    verification_case_name
                                ][idx][datapoint_info[key]["subject"]],
                                "variable": datapoint_info[key]["variable"],
                                "frequency": "",
                            }
                        )
                    else:
                        verification_case_dict_copy["datapoints_source"][
                            "idf_output_variables"
                        ][point_nonmen].update(
                            {
                                "subject": self.queried_datapoint_all_dict[
                                    verification_case_name
                                ][idx][datapoint_info[key]["subject"]],
                                "variable": self.queried_datapoint_all_dict[
                                    verification_case_name
                                ][idx][datapoint_info[key]["variable"]],
                                "frequency": "",
                            }
                        )
            verification_case_saving_list.append(verification_case_dict_copy)

        return verification_case_saving_list
