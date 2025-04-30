from constrain.workflowsteps import *
from constrain.library import *
from pathlib import Path
import json
import pandas as pd


items_json = "./library/library.json"


def get_verification_cases(cases_json):
    items = assemble_verification_items(
        cases_path=cases_json, lib_items_path=items_json
    )
    return items


def run_test_verification_with_data(verification_class, df, tolerances=None):
    cls = globals()[verification_class]
    if tolerances is None:
        path_to_custom_tolerance_file = Path(__file__).parent / "tolerances.json"
        with open(path_to_custom_tolerance_file) as f:
            tolerances = json.load(f)
    verification_obj = cls(df, None, tolerances=tolerances)
    return verification_obj


def main():
    # for dev test only
    points = [
        "number_occupants",
        "flow_volumetric_air_outdoor",
        "flow_volumetric_air_exhaust",
        "status_economizer",
    ]
    data = [[0, 1, 0, 0.001]]
    df = pd.DataFrame(data, columns=points)
    case_str = """
{
        "expected_result": "pass",
        "datapoints_source": {
            "test_variables": {
                "number_occupants": {},
                "flow_volumetric_air_outdoor": {},
                "flow_volumetric_air_exhaust": {},
                "status_economizer": {}
            },
            "parameters": {}
        },
        "verification_class": "AutomaticOADamperControl"
    }
    """
    case = json.loads(case_str)
    results = run_test_verification_with_data("AutomaticOADamperControl", df)
    print(results)


if __name__ == "__main__":
    main()
