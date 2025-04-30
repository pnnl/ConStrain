import json
from constrain.workflowsteps import *
from constrain.library import *
from constrain.libcases import *

# %% Load and assemble verification items
batch_size = 50
run_no_sim_cases = False
cases_path = "../test_cases/verif_mtd_pp/verification_cases.json"
print(f"Split verification cases by model with batch size of {batch_size}...")

with open(cases_path) as cases_file:
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

print("Saving files:")
for k, v in unique_idfs_to_items.items():
    batches = [v[i : i + batch_size] for i in range(0, len(v), batch_size)]
    j = 0
    for one_batch in batches:
        print(k)
        writer_path = f"../test_cases/verif_mtd_pp/{k.split('.idf')[0].split('/')[-1]}_Batch{j}.json"
        with open(writer_path, "w") as fw:
            json.dump({"cases": one_batch}, fw, indent=4)
        j += 1

if run_no_sim_cases:
    with open("../test_cases/verif_mtd_pp/no_idfs_items.json", "w") as fw:
        json.dump({"cases": no_idfs_items}, fw, indent=4)
else:
    print("Ignore cases that do not need simulation")
print("Complete!")
