"""Modules contains implemented methods for each sequential workflow step
Method typing is used to enforce designed Workflow I/O """

from typing import List
from constrain.item import Item
from constrain.datapoint import IdfOutputPoint
from constrain.ashrae import ASHRAEJsonReader
from constrain.epinjector import IDFInjector
from constrain.eprunner import EPRunner
from constrain.testbuilder import Testbuilder
import pandas as pd
from datetime import datetime
import json, logging


def read_json_file(jsonpath: str) -> List[dict]:
    """read json file and return a list of items, handle all items

    Args:
        jsonpath: json file path

    Returns:
        object: list of items, each one in terms of a `dict`

    """
    ashrae_json = ASHRAEJsonReader(json_file_path=jsonpath)
    ashrae_items = ashrae_json.items
    return ashrae_items


def build_an_item(item: dict) -> Item:
    """build an Item from the item dict, handle one item

    Args:
        item: item `dict`

    Returns:
        `Item` instance

    """
    item_instance = Item(item)
    return item_instance


def read_injection_points(item: Item) -> List[IdfOutputPoint]:
    """read idf output points to be injected from each item, handle one item

    Args:
        item: `Item` instance

    Returns:
        list of `IdfOutputPoint` for one item

    """
    idf_output_point_list = [
        p for p in item.buildpoints if isinstance(p, IdfOutputPoint)
    ]
    return idf_output_point_list


def combine_injection_points(
    unmerged_output_points: List[IdfOutputPoint],
) -> List[IdfOutputPoint]:
    """combine idf output points to eliminate duplicates, handle all items

    Args:
        unmerged_output_points: combined list of `IdfOutputPoint` objects from all items, duplicates may exist

    Returns:
        list of 'IdfOutputPoint' objects from all items, no duplicates

    """
    return list(set(unmerged_output_points))


def inject_idf(
    iddpath: str, idfpath_in: str, objstoinject: List[IdfOutputPoint], idfpath_out=None
) -> None:
    """inject output points to idf, handle all items

    Args:
        iddpath: path to the idd file
        idfpath_in: path to the original idf file
        objstoinject: list of unique 'IdfOutputPoint' objects to be injected in the idf file
        idfpath_out: path to save the injected idf file, by default set to None, which will overwrite the original idf

    """
    injector = IDFInjector(idf_file_in=idfpath_in, idd_file=iddpath)
    injector.inject_idf_outputs(eppy_output_objs=objstoinject)
    injector.save(idf_file_out=idfpath_out)


def run_simulation(idfpath: str, weatherpath: str, ep_path: str) -> None:
    """run energyplus simulation, handle all items

    Args:
        idfpath: path to the idf for energyplus simulation
        weatherpath: path to the weather file used for simulation
        ep_path: path to energyplus folder

    """
    eprun = EPRunner(idf_path=idfpath, weather_path=weatherpath, ep_path=ep_path)
    print(f"Running simulation: {idfpath} -- {datetime.now()}")
    eprun.run_simulation()
    print(f"Simulation complete -- {datetime.now()}")
    eprun.save_log()
    print(f"Simulation log saved to output folder -- {datetime.now()}")


def read_points(
    runpath: str, csv_filename: str, idf_filename: str, idd_path: str, item: Item
) -> pd.DataFrame:
    """read all types of data points values from simulation files, handle one item

    Args:
        runpath: path to the output folder
        csv_filename: csv file name in the output folder
        idf_filename: idf file name in the output folder
        idd_path: idd file path (not in the output folder)
        item: `Item` object

    Returns:
        pandas dataframe containing timeseries of all points, scalor type points already populated to time series

    """

    csv = runpath + "/" + csv_filename
    idf = runpath + "/" + idf_filename

    # TODO add item (filled with values by the read_points_values) to the return
    return item.read_points_values(csv_path=csv, idf_path=idf, idd_path=idd_path)


def run_rules(item: Item, pointsdf: pd.DataFrame):
    """run time series in the dataframe against the rule, handle one item

    designed to run with multiple asserstions if being contained in one item, only tested with one assertion

    Args:
        item: `Item` object
        pointsdf: pandas dataframe containing timeseries of all points

    Returns:
        dict of run results, keys are the assertions string, value lists length equal to time series length
        time series dataframe with assersion results appended as columns

    """
    tester = Testbuilder(pointsdf, item)
    results = tester.run_all()
    return results, tester.df


def assemble_verification_items(
    cases_path: str = None, lib_items_path: str = None, cases: dict = None
) -> List:
    """Assemble verification items from cases json and library item json.

    Args:
        cases_path (str): path to verification cases json file
        lib_items_path (str): path to library item json file

    Returns:
        List: list of assembled verification items
    """
    if isinstance(cases_path, str):
        with open(cases_path) as cases_file:
            cases_dict = json.load(cases_file)
    elif isinstance(cases, dict):
        if len(cases) > 0:
            cases_dict = {"cases": [cases]}
        else:
            logging.error("No item to assemble.")
    else:
        logging.error("No item to assemble.")
    with open(lib_items_path) as lib_items_file:
        lib_items_dict = json.load(lib_items_file)

    items = []
    for case in cases_dict["cases"]:
        case_verification_class = case["verification_class"].strip()
        case_verification_dict = lib_items_dict[case_verification_class]
        items.append({**case, **case_verification_dict})

    return items


def main():
    """testing code for the whole workflow, work with one item."""
    wosim = True
    idd_path = "../resources/Energy+V9_0_1.idd"
    items = read_json_file("../schema/item2_poc.json")
    print("Workflow: Json File Read Complete")
    # print(items)

    item = build_an_item(items[0])
    print("Workflow: Items Build Complete")
    # print(item.__dict__)
    # print(item.buildpoints[0].__dict__)

    idf_outputs = []
    idf_outputs.extend(read_injection_points(item))
    print("Workflow: Output Extraction Complete")
    print(
        f"A total of {len(idf_outputs)} EP Output variables objecs are extracted from {len(items)} items"
    )

    unique_output = combine_injection_points(idf_outputs)
    idf_final = "../resources/ASHRAE901_SchoolPrimary_STD2004_ElPaso_Injected.idf"
    print(
        f"{len(unique_output)} unique output variables will be added to file: {idf_final}"
    )

    inject_idf(
        iddpath="../resources/Energy+V9_0_1.idd",
        idfpath_in="../resources/ASHRAE901_SchoolPrimary_STD2004_ElPaso.idf",
        objstoinject=unique_output,
        idfpath_out=idf_final,
    )
    print("Workflow: Injection Complete")

    if wosim:
        print("Simulation Skipped, already completed (Use in Dev)")
    else:
        run_simulation(
            idfpath=idf_final,
            weatherpath="../weather/USA_TX_El.Paso.Intl.AP.722700_TMY3.epw",
        )
        print("Workflow: simulation complete")

    df = read_points(
        runpath="../resources/ASHRAE901_SchoolPrimary_STD2004_ElPaso_Injected",
        idf_filename="in.idf",
        csv_filename="eplusout.csv",
        idd_path=idd_path,
        item=item,
    )

    print(f"Points Read Complete, data frame contains {df.columns.tolist()}")
    print(df.head())

    results, testerdf = run_rules(item, df)
    # print(results)
    print(len(results))
    print(sum(results))
    print(
        testerdf[testerdf["$OA_timestep > $OA_min_sys and $Cool_sys_out > 0"] is True][
            testerdf.columns[0:4]
        ].head()
    )
    print(
        testerdf[testerdf["$OA_timestep > $OA_min_sys and $Cool_sys_out > 0"] is False][
            testerdf.columns[0:4]
        ].head()
    )


if __name__ == "__main__":
    main()
