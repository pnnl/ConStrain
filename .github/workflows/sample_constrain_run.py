import json, os, requests
import constrain as cs
from pathlib import Path
#if __name__ == "__main__":
#    examples = cs.Examples()
#    data = examples.data("example_1")
#    cases = cs.api.VerificationCase(json_case_path=examples.verifications("example_1"))
#    cases.validate()
#    verif = cs.api.Verification(verifications=cases)
#    verif.configure(
#        output_path="./",
#        lib_items_path=examples.library(),
#        plot_option="all-expand",
#        fig_size=(10, 5),
#        num_threads=1,
#        preprocessed_data=data,
#    )
#    verif.run()
#    reporting = cs.api.Reporting(
#        verification_json="./*_md.json",
#        result_md_name="report_summary.md",
#        report_format="markdown",
#    )
#
#    reporting.report_multiple_cases()


url = 'https://raw.githubusercontent.com/pnnl/ConStrain/refs/heads/develop/constrain/demo/G36_demo/G36_demo_workflow.json'
response = requests.get(url)
data = json.loads(response.content)

# Change data path
data["states"]["load data"]["Parameters"]["data_path"] = str(Path(__file__).parent.parent.parent / "/demo/G36_demo/data/G36_Modelica_Jan.csv")
data["states"]["load verification cases"]["Parameters"]["json_case_path"] = str(Path(__file__).parent.parent.parent / "/demo/G36_demo/data/G36_library_verification_cases.json")
data["states"]["configure verification runner"]["Parameters"]["output_path"] = "./"
data["states"]["configure verification runner"]["Parameters"]["lib_items_path"] = str(Path(__file__).parent.parent.parent / "constrain/schema/library.json")
data["states"]["check results"]["Parameters"][0] = "./*_md.json"
data["states"]["reporting_object_instantiation"]["Parameters"]["verification_json"] = "./*_md.json"

workflow = cs.Workflow(workflow=data)
workflow.run_workflow(verbose=True)

assert os.path.isfile("./case-1.md")
assert os.path.isfile("./case-2.md")
assert os.path.isfile("./case-3.md")
assert os.path.isfile("./report_summary.md")