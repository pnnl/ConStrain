import ast
import copy
import json
import logging
import os
import re
import sys
from collections import defaultdict

import brickschema
import yaml
from pydash import filter_, flatten_deep

sys.path.append("..")

HVAC_ZONE_NAME_PARSE_RE = r"\?(\w+) a brick:HVAC_Zone \."
CASE_KEY_NAMES = [
    "no",
    "run_simulation",
    "simulation_IO",
    "idf",
    "idd",
    "weather",
    "output",
    "ep_path",
    "expected_result",
    "parameters",
]


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
                the datapoint conversion name saving yaml file. The default path nis `./resources/brick/verification_datapoint_info.yml`.
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

        # check if the files exist in the given directory
        if not os.path.exists(brick_schema_path):
            logging.error(
                f"The file doesn't exist in the provided directory. Please make sure to provide a correct `brick_schema_path`."
            )
            return None

        if not os.path.exists(brick_instance_path):
            logging.error(
                f"The file doesn't exist in the provided directory. Please make sure to provide a correct `brick_instance_path`."
            )
            return None

        # define variables
        self.brick_schema_path = brick_schema_path
        self.brick_instance_path = brick_instance_path

        self.queried_datapoint_all_dict = defaultdict(list)
        self.queried_result_in_verification_form = []
        self.idx = 1

        self.verification_case_dict = {
            "no": None,
            "run_simulation": None,
            "simulation_IO": {
                "idf": "",
                "idd": "",
                "weather": "",
                "output": "",
                "ep_path": "",
            },
            "expected_result": "",
            "datapoints_source": {},
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
                f"The query statement file isn't found. Please verify the {query_statement_path} path."
            )
            return None

        # find all the HVAC_ZONE brick class names
        self.hvac_zone_name_container = list(
            set(
                flatten_deep(
                    [
                        re.findall(
                            HVAC_ZONE_NAME_PARSE_RE,
                            self.query_statement[verification_lib_name],
                        )
                        for verification_lib_name in self.query_statement
                    ]
                )
            )
        )

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

    def validate_brick_instance(self):
        """Validate a brick instance against the brick schema.

        Returns:
            valid: bool
                whether the validation passes/fails

            resultsText: str
                Message from the validation process

        """

        valid, _, resultsText = self.g.validate()

        return valid, resultsText

    def get_applicable_verification_lib_items(
        self,
        verification_lib_item_list: list = None,
    ):
        """Get applicable control verification library items among the `verification_item_lib_name` list from the brick instance.

        Args:
            verification_item_lib_name: list
                list of verification item names to be tested. If empty list is provided, all the available verification library items are tested.

        Returns: list
            list that includes available verification library item names from the given brick instance.

        """

        # check arg types
        if verification_lib_item_list is None:
            verification_lib_item_list = []
        elif not isinstance(verification_lib_item_list, list):
            logging.error(
                f"The `verification_lib_item_list` argument type must be list, but {type(verification_lib_item_list)} type is provided."
            )
            return None

        # determine total verification lib items to iterate. If `verification_lib_item_list` is empty, all the available verification items are used
        if verification_lib_item_list:
            # check if the given verification lib item names are valid
            if not set(verification_lib_item_list).issubset(list(self.query_statement)):
                logging.error(
                    f"The given verification library item names are invalid. Please check the names again."
                )
                return None

            verification_lib_items = verification_lib_item_list
        else:
            verification_lib_items = list(self.query_statement)

        # find if queried datapoints are the same as the datapoints in the library.json. If not, warning meesage shows up
        available_verification_item_list = []
        for verification_lib_item in verification_lib_items:
            for query_result in self.query_verification_case_datapoints(
                verification_lib_item
            ):
                try:
                    queried_datapoints = set(
                        query_result["datapoints_source"]["idf_output_variables"]
                    )
                except KeyError:
                    queried_datapoints = set(
                        query_result["datapoints_source"]["dev_settings"]
                    )
                lib_datapoints = set(
                    self.library_json[verification_lib_item]["description_datapoints"]
                )
                if queried_datapoints != lib_datapoints:
                    diff_datapoints = lib_datapoints - queried_datapoints
                    str_of_datapoints = ", ".join(str(item) for item in diff_datapoints)
                    logging.warning(
                        f"Please make sure {str_of_datapoints} datapoints are included in the verification case."
                    )
                else:
                    available_verification_item_list.append(verification_lib_item)

        return list(set(available_verification_item_list))

    def query_verification_case_datapoints(
        self,
        verification_item_lib_name: str,
        energyplus_naming_assembly: bool = True,
        default_verification_case_values: dict = None,
    ) -> list:
        """
        Query data point(s) for the given verification case.

        Args:
            verification_item_lib_name: str
                verification item name(s) that will be queried

            energyplus_naming_assembly: bool
                whether the queried datapoint is changed to E+ style variable name or not

            default_verification_case_values: dict
                default key values. ("no", "run_simulation", "idf", "idd", "weather", "output", "ep_path", "expected_result", "parameters",) keys must exist.

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

        if (
            not isinstance(default_verification_case_values, (dict, str))
            and default_verification_case_values is not None
        ):
            logging.error(
                f"The `default_verification_case_values` argument type must be dict or str, but {type(default_verification_case_values)} type is provided."
            )
            return None
        elif isinstance(default_verification_case_values, str):
            default_verification_case_values = ast.literal_eval(
                default_verification_case_values
            )

        # check if `default_verification_case_values` includes not allowed key(s)
        if default_verification_case_values is not None:
            self._default_verification_case_values_sanity_check_helper(
                default_verification_case_values
            )

        # perform query
        query_result = self.g.query(self.query_statement[verification_item_lib_name])

        # organize query result
        queried_verification_datapoints = self._organize_query_results_helper(
            query_result,
            verification_item_lib_name,
            energyplus_naming_assembly,
            default_verification_case_values,
        )

        # add to the `self.queried_result_in_verification_form`
        self.queried_result_in_verification_form += queried_verification_datapoints

        return queried_verification_datapoints

    def query_with_customized_statement(
        self,
        custom_query_statement: str,
        verification_item_lib_name: str,
        energyplus_naming_assembly: bool = True,
        default_verification_case_values: dict = None,
    ) -> list:
        """Query datapoints with a customized query statement. When implemented, the quality check of the `query_statement` is done by checking whether the number of queried variables are the same as the required number of data points in the verification library item.

        Args:
            custom_query_statement: str
                query statement written from users

            verification_item_lib_name: str
                verification library item of the query_statement

            energyplus_naming_assembly: bool
                whether to convert the queried datapoints' name to EnergyPlus style variable name.

            default_verification_case_values: dict
                default key values. ("no", "run_simulation", "idf", "idd", "weather", "output", "ep_path", "expected_result", "parameters",) keys must exist.

        Returns:
            queried result in the verification case format. `str` message from the `query_statement`'s quality check result.

        """
        # check arg types
        if not isinstance(custom_query_statement, str):
            logging.error(
                f"The `custom_query_statement` argument type must be str, but {type(custom_query_statement)} type is provided."
            )
            return None

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

        if (
            not isinstance(default_verification_case_values, (dict, str))
            and default_verification_case_values is not None
        ):
            logging.error(
                f"The `default_verification_case_values` argument type must be dict or str, but {type(default_verification_case_values)} type is provided."
            )
            return None
        elif isinstance(default_verification_case_values, str):
            default_verification_case_values = ast.literal_eval(
                default_verification_case_values
            )

        # check if `default_verification_case_values` includes not allowed key(s)
        if default_verification_case_values is not None:
            self._default_verification_case_values_sanity_check_helper(
                default_verification_case_values
            )

        # perform query
        query_result = self.g.query(custom_query_statement)

        # organize query result
        queried_verification_datapoints = self._organize_query_results_helper(
            query_result,
            verification_item_lib_name,
            energyplus_naming_assembly,
            default_verification_case_values,
        )

        # add to the `self.queried_result_in_verification_form`
        self.queried_result_in_verification_form += queried_verification_datapoints

        # quality check - whether the no. of queried variables == required no. of data points in the verification library item
        total_no_of_datapoints = len(
            self.library_json[verification_item_lib_name]["description_datapoints"]
        )

        for queried_datapoints in self.queried_datapoint_all_dict[
            verification_item_lib_name
        ]:
            if filter_(
                self.hvac_zone_name_container, lambda x: x in queried_datapoints
            ):
                if len(queried_datapoints) != total_no_of_datapoints + 1:
                    logging.warning(
                        f"The number of datapoints with the customized query statement is {len(queried_datapoints)-1} excluding the `hvac_zone` and the number of required datapoints for {verification_item_lib_name} verification item is {total_no_of_datapoints}. The two numbers must be the same."
                    )
            else:
                if len(queried_datapoints) != total_no_of_datapoints:
                    logging.warning(
                        f"The number of datapoints with the customized query statement is {len(queried_datapoints)} and the number of required datapoints for {verification_item_lib_name} verification item is {total_no_of_datapoints}. The two numbers must be the same."
                    )

        return queried_verification_datapoints

    def _organize_query_results_helper(
        self,
        query_result,
        verification_item_lib_name: str,
        energyplus_naming_assembly: bool,
        default_verification_case_values: dict = None,
    ):
        # save the data point name in the instance
        for row in query_result:
            queried_datapoint_dict = {}
            for i in range(len(row)):
                queried_datapoint_dict[list(row.labels)[i]] = row[i].split("#")[1]

            ver_item_datapoint_ver_item_lib = self.queried_datapoint_all_dict[
                verification_item_lib_name
            ]
            if queried_datapoint_dict not in ver_item_datapoint_ver_item_lib:
                ver_item_datapoint_ver_item_lib.append(queried_datapoint_dict)

        # convert to the verification case format
        result = self._convert_to_verification_case_format_helper(
            verification_item_lib_name,
            energyplus_naming_assembly,
            default_verification_case_values,
        )

        return result

    def _convert_to_verification_case_format_helper(
        self,
        verification_case_name: str,
        energyplus_naming_assembly: str,
        default_verification_case_values: dict = None,
    ) -> list:
        if energyplus_naming_assembly:
            self.verification_case_dict["datapoints_source"][
                "idf_output_variables"
            ] = {}
        else:
            self.verification_case_dict["datapoints_source"]["dev_settings"] = {}

        verification_case_saving_list = []
        for index, query_dict in enumerate(
            self.queried_datapoint_all_dict[verification_case_name]
        ):
            verification_case_dict_copy = copy.deepcopy(self.verification_case_dict)

            verification_case_dict_copy["no"] = self.idx
            self.idx += 1
            verification_case_dict_copy["verification_class"] = verification_case_name

            conversion_setting = (
                "EnergyPlus" if energyplus_naming_assembly else "default"
            )
            datapoint_info = self.verification_datapoint_info[verification_case_name][
                conversion_setting
            ]

            for key, value in query_dict.items():
                if (
                    key not in self.hvac_zone_name_container
                ):  # prevent HVAC_ZONE class from going through this loop
                    point_nonmen = datapoint_info[key]["point"]
                    if energyplus_naming_assembly:
                        verification_case_dict_copy["datapoints_source"][
                            "idf_output_variables"
                        ][point_nonmen] = {}
                    else:
                        verification_case_dict_copy["datapoints_source"][
                            "dev_settings"
                        ][point_nonmen] = {}

                    datapoint_ver_case_idx = self.queried_datapoint_all_dict[
                        verification_case_name
                    ][index]

                    try:
                        subject = datapoint_ver_case_idx[datapoint_info[key]["subject"]]
                    except KeyError:
                        subject = None

                    if energyplus_naming_assembly:
                        verification_case_dict_copy["datapoints_source"][
                            "idf_output_variables"
                        ][point_nonmen].update(
                            {
                                "subject": "" if subject is None else subject,
                                "variable": datapoint_info[key]["variable"],
                                "frequency": "",
                            }
                        )
                    else:
                        verification_case_dict_copy["datapoints_source"][
                            "dev_settings"
                        ][point_nonmen].update(
                            {
                                "subject": "" if subject is None else subject,
                                "variable": datapoint_ver_case_idx[
                                    datapoint_info[key]["variable"]
                                ],
                                "frequency": "",
                            }
                        )

            # feed in the default values if exist
            if default_verification_case_values is not None:
                verification_case_dict_copy[
                    "run_simulation"
                ] = default_verification_case_values["run_simulation"]

                for key_name in (
                    "idf",
                    "idd",
                    "weather",
                    "output",
                    "ep_path",
                ):
                    verification_case_dict_copy["simulation_IO"][
                        key_name
                    ] = default_verification_case_values["simulation_IO"][key_name]

                verification_case_dict_copy[
                    "expected_result"
                ] = default_verification_case_values["expected_result"]
                verification_case_dict_copy["datapoints_source"][
                    "parameters"
                ] = default_verification_case_values["parameters"]

            verification_case_saving_list.append(verification_case_dict_copy)

        return verification_case_saving_list

    def _default_verification_case_values_sanity_check_helper(
        self, default_verification_case_values: dict
    ) -> None:
        def _check_specific_keys_in_nested_dict(keys, dictionary):
            for key in dictionary:
                if key not in keys:
                    return False
                if isinstance(dictionary[key], dict) and key != "parameters":
                    if not _check_specific_keys_in_nested_dict(keys, dictionary[key]):
                        return False
            return True

        if not _check_specific_keys_in_nested_dict(
            CASE_KEY_NAMES, default_verification_case_values
        ):
            logging.error(
                f"`default_verification_case_values` dictionary includes NOT allowed key(s). Please verify the dictionary again."
            )
            return None
