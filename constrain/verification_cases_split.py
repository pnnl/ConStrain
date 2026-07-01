import json
from constrain.workflowsteps import *
from constrain.library import *
from constrain.libcases import *
import logging

# %% Load and assemble verification items
BATCH_SIZE = 50
RUN_NO_SIM_CASE = False
CASES_PATH = "../test_cases/verif_mtd_pp/verification_cases.json"
logging.info(f"Split verification cases by model with batch size of {BATCH_SIZE}...")

with open(CASES_PATH) as cases_file:
    cases_dict = json.load(cases_file)
items = [case for case in cases_dict["cases"]]

unique_idfs_to_items = {}
no_idfs_items = []
i = 0
for item in items:
    idf_path = None
    if item["run_simulation"]:
        idf_path = item["simulation_IO"]["idf"]
        if idf_path not in unique_idfs_to_items:
            unique_idfs_to_items[idf_path] = []
        unique_idfs_to_items[idf_path].append(item)
    else:
        no_idfs_items.append(item)

logging.info("Saving files:")
for k, v in unique_idfs_to_items.items():
    batches = [v[i : i + BATCH_SIZE] for i in range(0, len(v), BATCH_SIZE)]
    j = 0
    for one_batch in batches:
        logging.info(k)
        writer_path = f"../test_cases/verif_mtd_pp/{k.split('.idf')[0].split('/')[-1]}_Batch{j}.json"
        with open(writer_path, "w") as fw:
            json.dump({"cases": one_batch}, fw, indent=4)
        j += 1

if RUN_NO_SIM_CASE:
    with open("../test_cases/verif_mtd_pp/no_idfs_items.json", "w") as fw:
        json.dump({"cases": no_idfs_items}, fw, indent=4)
else:
    logging.info("Ignore cases that do not need simulation")
logging.info("Complete!")
