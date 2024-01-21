from constrain.workflowsteps import *
from constrain.library import *
import json
import pandas as pd

items_json = "./library/library.json"


def get_verification_cases(cases_json):
    items = assemble_verification_items(
        cases_path=cases_json, lib_items_path=items_json
    )
    return items


def run_test_verification_with_data(verification_class, df):
    # item = build_an_item(case)
    # verification_class = item.item["verification_class"]
    cls = globals()[verification_class]  # consultant says use map instead of globals
    # parameters = (
    #     item.item["datapoints_source"]["parameters"]
    #     if ("parameters" in item.item["datapoints_source"])
    #     else None
    # )
    verification_obj = cls(df, None)
    # verification_obj = cls(df, parameters)
    return verification_obj


def main():
    # for dev test only
    points = ["o", "m_oa", "eco_onoff", "tol"]
    data = [[0, 1, 0, 0.001]]
    df = pd.DataFrame(data, columns=points)
    case_str = """
{
        "expected_result": "pass",
        "datapoints_source": {
            "test_variables": {
                "o": {},
                "m_oa": {},
                "eco_onoff": {}
            },
            "parameters": {
                "tol": 24.0
            }
        },
        "verification_class": "AutomaticOADamperControl"
    }
    """
    case = json.loads(case_str)
    results = run_test_verification_with_data("AutomaticOADamperControl", df)
    print(results)


if __name__ == "__main__":
    main()
