"""
verification_case.py
====================================
Verification Case API
"""

import sys, os, logging, glob, json, uuid, copy

from typing import Dict, List, Tuple, Union

sys.path.append("..")


class VerificationCase:
    def __init__(self, cases: List = None, json_case_path: str = None) -> None:
        """Instantiate a verification case class object and load verification case(s) in `self.case_suite` as a Dict. keys are automatically generated unique id of cases, values are the fully defined verification case Dict. If any argument is invalid, the object instantion will report an error message.

        Args:
            cases: (optional) A list of Dict. dictionary that includes verification case(s).
            json_case_path: (optional) str. path to the verification case file. If the path ends with `*.json`, then the items in the JSON file are loaded. If the path points to a directory, then verification cases JSON files are loaded.
        """
        self.case_suite = {}

        if self.check_type("cases", cases, List):
            for case in cases:
                unique_hash = str(uuid.uuid1())
                case["case_id_in_suite"] = unique_hash
                self.case_suite[unique_hash] = case

        if self.check_type("json_case_path", json_case_path, str):
            # check if json or directory path is provided
            if self.check_json_path_type(json_case_path):
                self.load_verification_cases_from_json(json_case_path)
            else:  # when directory path is provided
                # check if the directory exists
                if os.path.exists(json_case_path):
                    # find all the JSON files in json_case_path directory
                    json_file_names = glob.glob(os.path.join(json_case_path, "*.json"))

                    # check if no of json_file_names isn't 0
                    if json_file_names:
                        for file in json_file_names:
                            self.read_case(file)
                    else:
                        logging.warning(
                            "There is no JSON files in the given `json_case_path` directory."
                        )
                else:
                    logging.error(
                        f"The provided directory doesn't exist. Please make sure to provide a correct `json_case_path`."
                    )

    def load_verification_cases_from_json(
        self, json_case_path: str = None
    ) -> Union[List[str], None]:
        """Add verification cases from specified json file into self.case_suite. Cases that have already been loaded are ignored.

        Args:
            json_case_path: str, path to the json file containing fully defined verification cases.

        Returns:
          List, unique ids of verification cases loaded in self.case_suite
        """

        # check `json_case_path` type
        if self.check_type("json_case_path", json_case_path, str):
            # check if `json_case_path` exists
            if self.check_file("json_case_path", json_case_path):
                newly_added_hash = self.read_case(json_case_path)
            else:
                return None
        else:
            return None

        return newly_added_hash

    def save_case_suite_to_json(
        self, json_path: str = None, case_ids: List = []
    ) -> None:
        """Save verification cases to a dedicated file. If the `case_ids` argument is empty, all the cases in `self.case_suite` is saved. If `case_ids` includes specific cases' hash, only the hashes in the list are saved.

        Args:
            json_path: str. path to the json file to save the cases.
            case_ids: (optional) List. Unique ids of verification cases to save. By default, save all cases in `self.case_suite`. Default to an empty list.
        """

        if case_ids is None:
            case_ids = []

        # check `json_path` type
        if not self.check_type("json_path", json_path, str):
            return None

        # check `case_ids` type
        if not self.check_type("case_ids", case_ids, List):
            return None

        # save case(s) based on `case_ids` arg
        cases = []
        if len(case_ids) == 0:
            case_ids = list(self.case_suite.keys())

        for case_id in case_ids:
            if case_id in self.case_suite.keys():
                cases.append(self.case_suite[case_id])
            else:
                logging.warning(f"case_id {case_id} is not in self.case_suite!")

        # use the `save_verification_cases_to_json` method to save
        self.save_verification_cases_to_json(json_path, cases)

    @staticmethod
    def create_verification_case_suite_from_base_case(
        base_case: Dict = None,
        update_key_value: Dict = None,
        keep_base_case: bool = False,
    ) -> Union[List[Dict], None]:
        """Create slightly different multiple verification cases by changing keys and values as specified in `update_key_value`. if `keep_base_case` is set to True, the `base_case` is added to the first element in the returned list.

        Args:
            base_case: Dict. base verification input information.
            update_key_value: Dict. the same format as the `base_case` arg, but the updating fields consist of a list of values to be populated with.
            keep_base_case: (optional) bool. whether to keep the base case in returned list of verification cases. Default to False.

        Returns:
          List,  A list of Dict, each dict is a generated case from the base case.
        """

        # return all the updating value lists' length
        def _count_modifying_value_helper(update_key_value: Dict) -> List:
            len_modifying_values = []

            for key, value in update_key_value.items():
                if isinstance(value, dict):
                    len_modifying_values.extend(_count_modifying_value_helper(value))
                elif isinstance(value, list):
                    len_modifying_values.append(len(value))

            return len_modifying_values

        # update key/value based on `update_key_value` to `base_case`
        def _update_key_helper(
            update_key_value: Dict, casees: List, prev_level_key: str = None
        ) -> Tuple[Dict, str]:
            for key, value in update_key_value.items():
                if isinstance(value, dict):
                    prev_level_key = key
                    casees, prev_level_key = _update_key_helper(
                        value, casees, prev_level_key
                    )

                elif isinstance(value, list):
                    for idx, case in enumerate(casees):
                        if key in [
                            "no",
                            "run_simulation",
                            "expected_result",
                            "datapoints_source",
                            "verification_class",
                        ]:
                            case[key] = value[idx]
                        elif key in ["idf", "idd", "weather", "output", "ep_path"]:
                            case["simulation_IO"][key] = value[idx]

                        elif key in ["subject", "variable", "frequency"]:
                            case["datapoints_source"]["idf_output_variables"][
                                prev_level_key
                            ][key] = value[idx]

                        elif prev_level_key == "parameters":
                            case["datapoints_source"]["parameters"][key] = value[idx]
            return casees, prev_level_key

        # check `base_case` type
        if not isinstance(base_case, Dict):
            logging.error(
                f"The `base_case` argument type must be Dict, but {type(base_case)} type is provided."
            )
            return None

        # check `update_key_value` type
        if not isinstance(update_key_value, Dict):
            logging.error(
                f"The `update_key_value` argument type must be Dict, but {type(update_key_value)} type is provided."
            )
            return None

        # check `keep_base_case` type
        if not isinstance(keep_base_case, bool):
            logging.error(
                f"The `keep_base_case` argument must be bool, but {type(keep_base_case)} type is provided."
            )
            return None

        # check if all the lists of modifying values have the same length.
        len_of_each_modifying_list = _count_modifying_value_helper(update_key_value)
        if len(set(len_of_each_modifying_list)) != 1:
            logging.error(f"The length of modifying values in lists must be the same.")
            return None

        # deep-copy the base_case
        generated_base_cases_list = []
        for _ in range(len_of_each_modifying_list[0]):
            generated_base_cases_list.append(copy.deepcopy(base_case))

        # update the values based on `update_key_value` arg
        updated_base_cases_list = _update_key_helper(
            update_key_value, generated_base_cases_list
        )[0]

        # add base_case if `keep_base_case` set to True
        if keep_base_case:
            updated_base_cases_list.insert(0, base_case)

        return updated_base_cases_list

    @staticmethod
    def validate_verification_case_structure(
        case: Dict = None, verbose: bool = False
    ) -> bool:
        """Validate verification case structure (e.g., check whether `run_simulation`, `simulation_IO`, etc. exist or not). Check if required key / values pairs exist in the case. check if datatype of values are appropriate, e.g. file path is str.

        Args:
            case: dict. case information that will be validated.
            verbose: bool. whether to output verbose information. Default to False.

        Returns:
            Bool, indicating whether the case structure is valid or not.
        """

        def _validate_case_structure_helper(schema, instance, verbose) -> Union[bool]:
            for schema_key, schema_value in schema.items():
                # accommodate data points alike scenarios (random string key with required value structure)
                if schema_key == "*":
                    keys = list(instance.keys())
                else:
                    keys = [schema_key]

                for key in keys:
                    # check key match
                    if key not in instance:
                        logging.error(f"Missing required key '{key}' in {instance}")
                        return False

                    case_value = instance[key]

                    if isinstance(schema_value, dict):
                        # recursively check nested value
                        is_cases_valid = _validate_case_structure_helper(
                            schema_value, case_value, verbose
                        )
                        if not is_cases_valid:
                            return False
                    else:
                        # check leaf value match
                        # if require float, it can be int
                        if schema_value == float:
                            eligible_types = [int, float]
                        else:
                            eligible_types = [schema_value]

                        type_match_list = [
                            isinstance(case_value, sv) for sv in eligible_types
                        ]

                        if not any(type_match_list):
                            logging.error(
                                f"The type of '{key}' key must be {schema_value}, but {type(case_value)} is provided."
                            )
                            return False
                        else:
                            if verbose:
                                print(
                                    f"The type of {key} has the correct type {schema_value}"
                                )
            return True

        # check case type
        if not isinstance(case, Dict):
            logging.error(
                f"The case argument type must be dict, but {type(case)} is provided."
            )
            return None

        # check verbose type
        if not isinstance(verbose, bool):
            logging.error(
                f"The verbose argument type must be bool, but {type(verbose)} is provided."
            )
            return None

        case_schema = {
            "no": int,
            "run_simulation": bool,
            "simulation_IO": {
                "output": str,  # all other are optional when data is already there.
            },
            "expected_result": str,
            "datapoints_source": {
                # "idf_output_variables": {
                #     "*": {"subject": str, "variable": str, "frequency": str}
                # },
                "parameters": {"*": float},
            },
            "verification_class": str,
        }
        return _validate_case_structure_helper(case_schema, case, verbose)

    def validate(self):
        """Validate all verification cases in self.case_suite with validation logic in VerificationCase.validate_verification_case_structure()"""
        for k, v in self.case_suite.items():
            if not self.validate_verification_case_structure(v):
                return False
        return True

    @staticmethod
    def save_verification_cases_to_json(
        json_path: str = None, cases: list = None
    ) -> None:
        """Save verification cases to a dedicated file. The cases list consists of verification case dicts.

        Args:
            json_path: str. json file path to save the cases.
            cases: List. List of complete verification cases Dictionary to save.
        """
        # check `json_path` type
        if not isinstance(json_path, str):
            logging.error(
                f"The `json_path` argument type must be str, but {type(json_path)} is provided."
            )
            return None

        # check `cases` type
        if not isinstance(cases, list):
            logging.error(
                f"The `cases` argument type must be list, but {type(cases)} is provided."
            )
            return None

        # check if `json_path` extension is .json
        if not json_path[-5:] == ".json":
            logging.error(f"The `json_path` argument must end with '.json' extension.")
            return None

        # organize the cases in the correct format
        case_suite_in_template_format = {"cases": cases}

        # save the case suite
        with open(json_path, "w") as fw:
            json.dump(case_suite_in_template_format, fw, indent=4)

    def read_case(self, file_name: str) -> List:
        # load the cases from file_path
        with open(file_name, "r") as f:
            loaded_cases = json.load(f)

        newly_added_hash = []
        for loaded_case in loaded_cases["cases"]:
            # check if there is any duplicated case. If so, don't add the case to `self.case_suite`
            if not self.case_already_in_suite(case=loaded_case):
                unique_hash = str(uuid.uuid1())
                loaded_case["case_id_in_suite"] = unique_hash
                self.case_suite[unique_hash] = loaded_case
                newly_added_hash.append(unique_hash)

        return newly_added_hash

    @staticmethod
    def same_case(case_a: {}, case_b: {}, ignored_keys=["case_id_in_suite"]) -> bool:
        case_a_new = {k: v for k, v in case_a.items() if k not in ignored_keys}
        case_b_new = {k: v for k, v in case_b.items() if k not in ignored_keys}
        return case_a_new == case_b_new

    def case_already_in_suite(
        self, case: {}, ignored_keys=["case_id_in_suite"]
    ) -> bool:
        for k, v in self.case_suite.items():
            if self.same_case(case, v, ignored_keys=ignored_keys):
                return True
        return False

    @staticmethod
    def check_json_path_type(json_path: str) -> bool:
        return True if json_path[-5:] == ".json" else False

    @staticmethod
    def check_type(
        var_name: str, var_value: Union[str, list, dict], var_type: type
    ) -> bool:
        if var_value is None:
            # no error msg if None
            return False
        if not isinstance(var_value, var_type):
            logging.error(
                f"The `{var_name}` argument's type must be {var_type}, but {type(var_value)} is provided."
            )
            return False
        else:
            return True

    @staticmethod
    def check_file(file_path_name: str, file_path: str) -> bool:
        if os.path.isfile(file_path):
            return True
        else:
            logging.error(
                f"`{file_path}' doesn't exist. Please make sure that the '{file_path_name}' argument is correct."
            )
            return False
