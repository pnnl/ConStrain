import json, glob

md_dict_dump = {}

for md_file in glob.glob("../results/*_md.json"):
    with open(md_file) as fr:
        md_dict = json.load(fr)
    md_dict_intkey = {int(k): v for k, v in md_dict.items()}
    md_dict_dump.update(md_dict_intkey)

md_full_string0 = """
# Verification Results:

| Case No.               | Simulation Model                           | Verification Class | Sample # | Pass # | Fail # | Verification Passed? |
| ---------------------- | ------------------------------------------ | ------------------ | -------- | ------ | ------ | -------------------- |
"""

caseids_sorted = sorted(md_dict_dump)

for caseid in caseids_sorted:
    case_dict = md_dict_dump[caseid]
    outcome = case_dict["outcome_notes"]
    model_file = case_dict["model_file"]
    verification_class = case_dict["verification_class"]

    mdtable_row = f"| [{caseid}](./case-{caseid}.md) | {model_file} | {verification_class} | {outcome['Sample #']} | {outcome['Pass #']} | {outcome['Fail #']} | {outcome['Verification Passed?']} |\n"
    md_full_string0 += mdtable_row

    md_section = case_dict["md_content"]

    md_section += "[Back](results.md)"
    with open(f"../results/case-{caseid}.md", "w") as casew:
        casew.write(md_section)

md_full_string = md_full_string0

with open("../results/results.md", "w") as fw:
    fw.write(md_full_string)
