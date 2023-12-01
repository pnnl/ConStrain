"""
verification_library.py
====================================
Verification Library API
"""

import sys, logging, glob, json, inspect
from typing import Dict, List, Union

sys.path.append("..")
from constrain.library import *

library_schema = {
    "library_item_id": (int, str, float),
    "description_brief": str,
    "description_detail": str,
    "description_index": list,
    "description_datapoints": dict,
    "description_assertions": list,
    "description_verification_type": str,
    "assertions_type": str,
}


class VerificationLibrary:
    def __init__(self, lib_path: str = None):
        """Instantiate a verification library class object and load specified library items as `self.lib_items`.

        Args:
            lib_path (str, optional): path to the verification library file or folder. If the path ends with `*.json`, then library items defined in the json file are loaded. If the path points to a directory, then library items in all jsons in this directory and its subdirectories are loaded. Library item need to have unique name defined in the json files and python files. Defaults to None.

        """

        self.lib_items = {}
        self.lib_items_json_path = {}
        self.lib_items_python_path = {}

        # check argument
        if lib_path is None:
            logging.error(
                "'lib_path' was not provided when instantiating the Verificationlibrary class object!"
            )
            return None

        if not isinstance(lib_path, str):
            logging.error(
                f"lib_path needs to be str of library file or foler path. It cannot be a {type(lib_path)}"
            )
            return None

        # load lib
        lib_path = lib_path.strip()

        lib_files_json_dict = {}
        if lib_path.split(".")[-1] == "json":
            lib_items_files = glob.glob(lib_path)
        else:
            if lib_path[-1] != "/":
                lib_path = lib_path + "/"
            lib_items_files = glob.glob(f"{lib_path}**/*.json", recursive=True)

        if len(lib_items_files) == 0:
            logging.error(f"There is no json file in {lib_path}")
            return None

        for lib_items_file_path in lib_items_files:
            with open(lib_items_file_path) as lib_items_file:
                lib_files_json_dict[lib_items_file_path] = json.load(lib_items_file)

        # store items
        for k, v in lib_files_json_dict.items():
            shared_keys = list(set(self.lib_items).intersection(v))
            if len(shared_keys) > 0:
                logging.warning(
                    f"{len(shared_keys)} repeated verification item names identified when loading: {shared_keys}"
                )

            self.lib_items.update(v)
            for lib_name, lib_content in v.items():
                self.lib_items_json_path[lib_name] = k
                if lib_name in globals().keys():
                    python_path = inspect.getfile(globals()[lib_name])
                else:
                    python_path = "Not Found"
                    logging.warning(
                        f"Python class file of loaded library item {lib_name} Not Found in the library"
                    )
                self.lib_items_python_path[lib_name] = python_path

    def get_library_item(self, item_name: str) -> Dict:
        """Get the json definition and meta information of a specific library item.

        Args:
            item_name (str): Verification item name to get.

        Returns:
            Dict: Library item information with four specific keys:
                - `library_item_name`: unique str name of the library item.
                - `library_json`: library item json definition in the library json file.
                - `library_json_path`: path of the library json file that contains this library item.
                - `library_python_path`: path of the python file that contains the python implementation of this library item.
        """

        item_name = item_name.strip()

        if not item_name in self.lib_items.keys():
            logging.error(f"{item_name} is not in loaded library items.")
            return None

        item_dict = {
            "library_item_name": item_name,
            "library_definition": self.lib_items[item_name],
            "library_json_path": self.lib_items_json_path[item_name],
            "library_python_path": self.lib_items_python_path[item_name],
        }

        return item_dict

    def validate_library(self, items: List[str] = None) -> Dict:
        """Check the validity of library items definition. This validity check includes checking the completeness of json specification (against library json schema) and Python verification class definition (against library class interface) and the match between the json and python implementation.

        Args:
            items: list of str, default []. Library items to validate. `items` must be filled with valid verification item(s). If not, an error occurs.

        Returns:
            Dict that contains validity information of library items.
        """

        # check `items` type
        if not isinstance(items, list):
            logging.error(f"items needs to be list. It cannot be a {type(items)}.")
            return None

        # check if `items` is an empty list
        if not items:
            logging.error(
                f"items is an empty list. Please provide with verification item names."
            )
            return None

        validity_info = {}
        for item in items:
            validity_info[item] = {}

            # verify the library.json file
            for lib_key in library_schema.keys():
                # check if lib keys exist. "description_detail" key is optional
                if lib_key not in ["description_detail"] and not self.lib_items[
                    item
                ].get(lib_key):
                    logging.error(
                        f"{lib_key} doesn't exist. Please make sure to have {lib_key}."
                    )
                    return None

                # check if key is in the correct type
                try:
                    if not isinstance(
                        self.lib_items[item][lib_key], library_schema[lib_key]
                    ):
                        logging.error(
                            f"The type of `{lib_key}` key needs to be {str(library_schema[lib_key])}. It cannot be a {type(self.lib_items[item][lib_key])}."
                        )
                        return None

                    else:
                        validity_info[item][lib_key] = type(
                            self.lib_items[item][lib_key]
                        )

                except KeyError:
                    # if `description_detail` key doesn't exist, output a warning.
                    validity_info[item][lib_key] = None
                    logging.warning(f"{lib_key} doesn't exist.")

            # check if datapoints in library file and class are identical
            if (
                list(self.lib_items[item]["description_datapoints"].keys())
                != globals()[item].points
            ):
                logging.error(
                    f"{item}'s points in the library file and class implementation are not identical."
                )
                return None
            else:
                validity_info[item]["datapoints_match"] = True

        return validity_info

    def get_library_items(self, items: List[str] = []) -> Union[List, None]:
        """Get the json definition and meta information of a list of specific library items.

        Args:
            items:  list of str, default []. Library items to get. By default, get all library items loaded at instantiation.

        Returns:
            list of `Dict` with four specific keys:
                - `library_item_name`: unique str name of the library item.
                - `library_json`: library item json definition in the library json file.
                - `library_json_path`: path of the library json file that contains this library item.
                - `library_python_path`: path of the python file that contains the python implementation of this library item.
        """

        # check `items` arg type
        if not isinstance(items, List):
            logging.error(f"items' type must be List. It can't be {type(items)}.")
            return None

        # cause an error when `items` arg is empty
        if not items:
            logging.error(
                f"items' arg is empty. Please provide with verification item(s)."
            )
            return None

        # get each lib item's summary info
        item_list = []
        for item in items:
            item_list.append(self.get_library_item(item))

        return item_list

    def get_applicable_library_items_by_datapoints(
        self, datapoints: List[str] = []
    ) -> Dict:
        """Based on provided datapoints lists, identify potentially applicable library items from all loaded items. Use this function with caution as it 1) requires aligned data points naming across all library items; 2) does not check the topological relationships between datapoints.

        Args:
            datapoints: list of str datapoints names.

        Returns:
            Dict with keys being the library item names and values being the required datapoints for the corresponding keys.
        """

        # check `datapoints` type
        if not isinstance(datapoints, List):
            logging.error(
                f"datapoints' type must be List. It can't be {type(datapoints)}."
            )
            return None

        # check if `datapoints` is an empty list
        if not datapoints:
            logging.error(
                f"`datapoints' is an empty list. Please provide with datapoint names."
            )
            return None

        # check the type of elements in `datapoints`
        for datapoint in datapoints:
            if not isinstance(datapoint, str):
                logging.error(
                    f"element's type in the datapoints argument must be str. It can't be {type(datapoint)}."
                )
                return None

        # check if applicable lib(s) exists with the datapoints arg
        applicable_lib_dict = {}
        for lib_item in self.lib_items.keys():
            required_lib_datapoints = list(
                self.lib_items[lib_item]["description_datapoints"].keys()
            )
            if set(required_lib_datapoints).issubset(set(datapoints)):
                applicable_lib_dict[lib_item] = required_lib_datapoints

        return applicable_lib_dict

    def get_required_datapoints_by_library_items(
        self, datapoints: List[str] = []
    ) -> Union[Dict, None]:
        """Summarize datapoints that need to be used to support specified library items. Use this function with caution as it 1) requires aligned data points naming across all library items; 2) does not check the topological relationships between datapoints.

        Args:
            items: list of str, default []. Library items to summarize datapoints from. By default, summarize all library items loaded at instantiation.

        Returns:
            Dict with keys being the datapoint name and values being a sub Dict with the following keys:
                - number_of_items_using_this_datapoint: int, number of library items that use this datapoint.
                - library_items_list: List, of library item names that use this datapoint.
        """

        if not isinstance(datapoints, List):
            logging.error(
                f"The `datapoints` argument type must be List, but {type(datapoints)} type is provided."
            )
            return None

        # check if `datapoints` is an empty list
        if not datapoints:
            logging.error(
                f"`datapoints' is an empty list. Please provide with datapoint names."
            )
            return None

        req_datapionts_by_lib_items = {}
        for datapoint in datapoints:
            req_datapionts_by_lib_items[datapoint] = {
                "number_of_items_using_this_datapoint": 0,
                "library_items_list": [],
            }
            for item in self.lib_items.items():
                if datapoint in item[1]["description_datapoints"].keys():
                    req_datapoint_dict = req_datapionts_by_lib_items[datapoint]
                    req_datapoint_dict["number_of_items_using_this_datapoint"] += 1
                    req_datapoint_dict["library_items_list"].append(item[0])

        return req_datapionts_by_lib_items
