"""
examples.py
====================================
This modules provide helper functions to retrieve data and information for examples of ConStrain.
"""
import logging
from .api import DataProcessing

# TODO: move this to a JSON file
examples = {
    "example_1": {
        "description": "Perform verification of ASHRAE Guideline 36-2021 sequence of operation on a dataset generated through the simulation of an AHU in Modelica. The verifications include the following: supply temperature reset, outdoor air damper psition for relief damper/fan, and return air damper psition for relief damper/fan",
        "path_to_data": "./demo/G36_demo/data/G36_Modelica_Jan.csv",
        "path_to_verifications": "./demo/G36_demo/data/G36_library_verification_cases.json",
    }
}


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
        return "./schema/library.json"

    def verifications(self, example_name):
        if self.check_example(example_name):
            return self.info[example_name]["path_to_verifications"]
        else:
            return
