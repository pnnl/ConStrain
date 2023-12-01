"""
This file contains the runner of verification cases to be called by the user with the supply of an item and plotting option
"""
# %% Import packages
from constrain.workflowsteps import *
from constrain.library import *
from constrain.datetimeep import DateTimeEP
import sys, os


def run_libcase(
    item_dict,
    plot_option="all-compact",
    output_path="./",
    fig_size=(6.4, 4.8),
    produce_outputs=False,
    preprocessed_data=None,
):
    """Library case runner

    Args:
        item_dict (Dict): verification item dict loaded from json files through `assemble_verification_items`
        plot_option: result plotting option.
    """

    item = build_an_item(item_dict)
    print(f"===========\nRunning case - {item.item['verification_class']}\n===========")

    idf_outputs = []
    idf_outputs.extend(read_injection_points(item))
    unique_output = combine_injection_points(idf_outputs)

    if "idf_output_variables" in item.points.keys():
        need_injection = True
    else:
        need_injection = False
    run_sim = item.item["run_simulation"]

    run_idf_path = None
    idd_path = None
    run_path = None
    if need_injection:
        original_idf_path = item.item["simulation_IO"]["idf"].strip()
        idd_path = item.item["simulation_IO"]["idd"].strip()
        if ".idf" in original_idf_path.lower():
            run_path = f"{original_idf_path[:-4]}"
        elif ".epjson" in original_idf_path.lower():
            run_path = f"{original_idf_path[:-7]}"
        else:
            run_path = original_idf_path
        instrumented_idf_path = f"{original_idf_path.split('.idf')[0]}_injected_VerificationNo{item_dict['no']}.idf"
        run_path = f"{run_path}_injected_VerificationNo{item_dict['no']}"
        inject_idf(
            iddpath=idd_path,
            idfpath_in=original_idf_path,
            objstoinject=unique_output,
            idfpath_out=instrumented_idf_path,
        )
        run_idf_path = instrumented_idf_path
    elif run_sim:
        run_idf_path = original_idf_path

    if run_sim:
        weather_path = item.item["simulation_IO"]["weather"].strip()
        if "ep_path" in list(item.item["simulation_IO"].keys()):
            run_simulation(
                idfpath=run_idf_path,
                weatherpath=weather_path,
                ep_path=item.item["simulation_IO"]["ep_path"],
            )
        else:
            run_simulation(idfpath=run_idf_path, weatherpath=weather_path)
        print("Simulation done")

    if not preprocessed_data is None:
        df = item.read_points_values(
            idf_path=run_idf_path, idd_path=idd_path, df=preprocessed_data
        )
    elif run_sim:
        df = DateTimeEP(
            item.read_points_values(
                csv_path=f"{run_path}/eplusout.csv",
                idf_path=f"{run_path}/in.idf",
                idd_path=idd_path,
            ),
            year=2000,
        ).transform()
    else:
        df = DateTimeEP(
            item.read_points_values(
                csv_path=f"{instrumented_idf_path.replace('.idf', '')}/{item.item['simulation_IO']['output']}"
            )
        ).transform()
    verification_class = item.item["verification_class"]
    cls = globals()[verification_class]
    parameters = (
        item.item["datapoints_source"]["parameters"]
        if ("parameters" in item.item["datapoints_source"])
        else None
    )
    verification_obj = cls(df, parameters, f"{run_path}")
    if produce_outputs:
        md_content = verification_obj.add_md(
            None, output_path, "./", item_dict, plot_option, fig_size
        )
        return {int(item_dict["no"]): md_content}
    else:
        outcome = verification_obj.get_checks
        verification_obj.plot(plot_option)


def main():
    num_argv = len(sys.argv)
    # NOTE: all relative paths in the json files should be based on "./" being "./constrain"
    cases_path = "../test_cases/verif_mtd_pp/verification_cases.json"
    lib_items_path = "../schema/library.json"
    items = assemble_verification_items(
        cases_path=cases_path, lib_items_path=lib_items_path
    )
    if num_argv == 1:
        print(
            f"No command line argument provided, running all {len(items)} verification cases from {cases_path} sequentially with one thread"
        )
        for item in items:
            run_libcase(item_dict=item)
    elif num_argv == 2:
        case_no = int(sys.argv[1])
        print(f"Running verification case {case_no}")
        run_libcase(item_dict=items[case_no])
    else:
        print(f"Error: Invalid number of arguments provided: {sys.argv}")


if __name__ == "__main__":
    print(f"Running main() in {os.getcwd()}...")
    main()
    print("Running of main() completed!")
