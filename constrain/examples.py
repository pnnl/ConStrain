"""
examples.py
====================================
This modules provide helper functions to retrieve data and information for examples of ConStrain.
"""

import logging, pathlib, json
from .api import DataProcessing

path = pathlib.Path(__file__).parent.resolve()


# Load examples from JSON file
def _load_examples():
    examples_file = path / "examples.json"
    with open(examples_file, "r") as f:
        data = json.load(f)

    # Convert relative paths to absolute paths
    for example_name, example_data in data.items():
        if "path_to_data" in example_data:
            example_data["path_to_data"] = str(path / example_data["path_to_data"])
        if "path_to_verifications" in example_data:
            example_data["path_to_verifications"] = str(
                path / example_data["path_to_verifications"]
            )

    return data


examples = _load_examples()


class Examples:
    def __init__(self):
        self.info = examples

    def check_example(self, example_name):
        if example_name in self.info.keys():
            return True
        else:
            logging.error(
                f"{example_name} is not a valid example. Here are all the valid example names: {str(list(self.info.keys())).replace('[', '').replace(']', '')}."
            )
            return False

    def data(self, example_name):
        if self.check_example(example_name):
            return DataProcessing(
                data_path=self.info[example_name]["path_to_data"],
                data_source="EnergyPlus",
            ).data
        else:
            return

    def library(self):
        return f"{path}/schema/library.json"

    def verifications(self, example_name):
        if self.check_example(example_name):
            return self.info[example_name]["path_to_verifications"]
        else:
            return
