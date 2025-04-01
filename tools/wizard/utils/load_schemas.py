import json
import os
import sys


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


LIBRARY_PATH = get_resource_path("schema/library.json")


def load_verification_cases_library():
    return load_json(LIBRARY_PATH)


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)
