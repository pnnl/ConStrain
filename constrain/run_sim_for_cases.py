from constrain.workflowsteps import *
from constrain.library import *
from tqdm import tqdm
import sys, shutil


def run_sim_for_cases(
    cases_path, lib_items_path="../schema/library.json", batch_postfix=""
):
    items_dict = assemble_verification_items(
        cases_path=cases_path, lib_items_path=lib_items_path
    )
    items = [build_an_item(item_dict) for item_dict in items_dict]
    print("Merging idf output injection points...")
    idf_outputs = []
    for item in tqdm(items, desc="Reading injection points from cases"):
        idf_outputs.extend(read_injection_points(item))
    print(f"A total of {len(idf_outputs)} injection points extracted, Merging...")
    unique_output = combine_injection_points(idf_outputs)
    print(
        f"After merging, a total of {len(unique_output)} output points will be injected."
    )

    need_injection = True
    run_sim = True

    item = items[0]
    if need_injection and run_sim:
        original_idf_path = item.item["simulation_IO"]["idf"].strip()
        idd_path = item.item["simulation_IO"]["idd"].strip()
        wth_file = item.item["simulation_IO"]["weather"].strip()
        # run_path = f"{original_idf_path.split('.idf')[0]}"
        if ".idf" in original_idf_path.lower():
            run_path = f"{original_idf_path[:-4]}"
        elif ".epjson" in original_idf_path.lower():
            run_path = f"{original_idf_path[:-7]}"
        else:
            run_path = original_idf_path

    if need_injection:
        instrumented_idf_path = f"{original_idf_path.split('.idf')[0]}_{batch_postfix}_injected_BatchVerification.idf"
        run_path = f"{run_path}_injected_BatchVerification"
        if len(wth_file):
            shutil.copyfile(
                wth_file,
                f"{original_idf_path.split('.idf')[0]}_{batch_postfix}_injected_BatchVerification.epw",
            )
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
    # TODO: the following code block is temperarily commented out for PIC run. Need to be wrapped as an option for local run.
    #        if "ep_path" in list(item.item["simulation_IO"].keys()):
    #            run_simulation(
    #                idfpath=run_idf_path,
    #                weatherpath=weather_path,
    #                ep_path=item.item["simulation_IO"]["ep_path"],
    #            )
    #        else:
    #            run_simulation(idfpath=run_idf_path, weatherpath=weather_path)
    #        print("simulation done")
    print(f"Run path: {run_path}")
    return run_path


def main():
    num_argv = len(sys.argv)
    if num_argv == 1:
        print(
            "No command line argument provided. Error!\n Please provide cases_path and lib_items_path, both relative to the current run path (constrain/)"
        )
        cases_path = None
        lib_items_path = None
        return
    if num_argv == 2:
        cases_path = sys.argv[1]
        lib_items_path = "../schema/library.json"
        print(
            f"One command line argument provided.\nRunning verification cases in {cases_path}\nUsing default verification library json at {lib_items_path}"
        )
    if num_argv == 3:
        cases_path = sys.argv[1]
        lib_items_path = sys.argv[2]
        print(
            f"Two command line arguments provided.\nRunning verification cases in {cases_path}\nUsing default verification library json at {lib_items_path}"
        )
    postfix = cases_path.strip().replace(".json", "").split("_")[-1]
    run_sim_for_cases(
        cases_path=cases_path, lib_items_path=lib_items_path, batch_postfix=postfix
    )
    print("run_sim_for_cases DONE!")


if __name__ == "__main__":
    main()
