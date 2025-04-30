"""Module for importing and storing ashrae 90.1 rule items"""

import json


class ASHRAEJsonReader:
    """Reads the json file and store the items for evaluation

    Attributes:
        json_file_path: path to the Json file containing ASHRAE 90.1 items specs
        json_data: dict loaded with json data
        items: list of ASHRAE 90.1 items, each is a dict containing corresponding specs
    """

    def __init__(self, json_file_path: str):
        """

        Args:
            json_file_path: path to the Json file containing ASHRAE 90.1 items specs
        """
        self.json_file_path = json_file_path
        self.json_data = self.read_json()
        self.items = self.get_item_list()

    def read_json(self):
        """constructor helper to read from external json files

        Returns:
            dict containing json spec

        """
        with open(self.json_file_path) as json_file:
            data = json.load(json_file)
        return data

    def get_item_list(self):
        """constructor helper to put the json items into a list.

        Returns:
            list of items

        """
        return self.json_data["items"]
