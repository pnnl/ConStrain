Quickstart Guide
=================

.. role:: python(code)
   :language: python
.. role:: json(code)
   :language: JSON
.. role:: bash(code)
   :language: bash

This guide provides a quick overview of how to get started with **ConStrain**. Verifications of building system control related timeseries using **ConStrain** can either be done by using **ConStrain** as a Python library or by using a **ConStrain** workflow.

What? Who? How?
------------------
**ConStrain** is a data-driven knowledge-integrated framework that automatically verifies that controls function as intended. As such, **ConStrain** might be of interest to a wide audience: from commissioning agents, to building operators, building energy modeling software users and developers and more. 

The first step towards using the tool is to gather timeseries data that can be used to verify a specific sequence of operation or the correct behavior of an equipment. **ConStrain**'s library_ provide a list of the different verifications that can be performed, not that they can it can be expanded see documentation section on that topic. For each, it provides some general description and references, and also provides a list of the data points needed to carry out verifications. For example, the ASHRAE Guideline 36 verification named `G36ReheatTerminalBoxDeadbandAirflowSetpoint` aims to very that terminal boxes with reheat when the zone state is deadband following the Guideline 36 recommendations as described in Section 5.6.5.2 in ASHRAE Guideline 36 2021. For this verification to be carried out, a user would have to gather timeseries (or static parameter values when applicable) for the following datapoints: system operation mode, zone state, minimum airflow setpoint during occupied mode, airflow setpoint, heating coil command, discharge air temperature, minimum discharge air temperature setpoint. Note that the timeseries can come from any sources: from a building management system or from simulation. When completed, one is ready to use ConStrain. Note that if the data needs to be pre-processed, **ConStrain**'s pre-processing API_ could help.

Installing **ConStrain**
-------------------------
**ConStrain** can be installed from PyPI by running the following command.

.. sourcecode:: bash

   pip install constrain

Running Verifications using **ConStrain**
------------------------------------------------------

**ConStrain** relies on verification case files to perform verifications. These are JSON files that contain all the necessary information about data points, reference to verification logics, and simulation parameters when applicable. A verification case file can be built as follows:

  1. Identify if the desired verification is already part of the default library. **ConStrain**'s default verifications are documented :doc:`here <../Verifications>`. If not, consider expanding the default verifications, help is provided :doc:`here <../Expand Exisiting Verifications>`.
  2. Create a JSON file that contains all the information needed by ConStrain to run the verification as detailed below or as defined in this schema_.
  3. Run the verification either using **ConStrain** as a :ref:`library <lib>` or using a **ConStrain** :ref:`workflow <wf>`.

.. sourcecode:: JSON

  {
      "cases": [
          {
              "no": 1,
              "run_simulation": false,
              "simulation_IO": {
                "idf": "modelica_dataset_set",
                "idd": "./resources/Energy+V9_0_1.idd",
                "weather": "./weather/USA_GA_Atlanta-Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
                "output": "./demo/G36_demo/data/G36_Modelica_Jan.csv",
                "ep_path": "C:\\EnergyPlusV9-0-1\\energyplus.exe"
              },
              "expected_result": "pass",
              "datapoints_source": {
                  "dev_settings": {
                      "heating_output": "heating_output",
                      "cooling_output": "cooling_output",
                      "ra_p": "ra_p",
                      "max_ra_p": "max_ra_p",
                      "oa_p": "oa_p",
                      "max_oa_p": "max_oa_p"
                  }
              },
              "verification_class": "G36ReturnAirDamperPositionForReliefDamperOrFan"
          }
      ]
  }

- :json:`"no"`: A verification case JSON file can contain multiple cases, this corresponds to the ID of a case
- :json:`"run_simulation"`: Is a flag (:json:`true` or :json:`false`) that indicates if an EnergyPlus simulation should be performed
- :json:`"simulation_IO"`: Is a dictionary that contains information about what reference files should be used for the simulation if a simulation is not required the :json:`"output"` is still required, it corresponds to the file that **ConStrain** will use to run verifications
- :json:`"expected_result"`: Expected result from the verification, either :json:`"pass"` or :json:`"fail"`
- :json:`"verification_class"`: Name of the verification from the library to carry out
- :json:`"datapoints_source"`: Dictionary that contains information on the data points used for the verification; They can be of different types: :json:`"parameters"` (constant values), :json:`"dev_settings"` (mapping of the expected datapoint for the verification to column headers in the data), or :json:`"idf_output_variables"` (for EnergyPlus-based simulations); The latter should be defined also as a dictionary where each variable is expressed through a :json:`"subject"` (EnergyPlus output variable name), :json:`"variable"` (EnergyPlus output variable type), and :json:`"frequency"` (EnergyPlus output variable reporting frequency), see an example below

.. sourcecode:: JSON

  "idf_output_variables": {
    "temperature_air_supply": {
      "subject": "VAV_1 Supply Equipment Outlet Node",
      "variable": "System Node Setpoint Temperature",
      "frequency": "detailed"
    }
  }

.. _lib:

Using **ConStrain** as a Python Library
----------------------------------------

First, let's import the package.

.. sourcecode:: python

    import constrain as cs

**ConStrain** includes an :python:`Examples` module which contains sample data and examples of verifications. Information about each example can be obtained by running the following command. A dictionary is returned which shows information about each example.

.. sourcecode:: python

    # Load examples
    examples = cs.Examples()
    
    # Get the data
    data = examples.info

Let's proceed with :python:`example_1` which according to its description aims to:

 *Perform verification of ASHRAE Guideline 36-2021 sequence of operation on a dataset generated through the simulation of an AHU in Modelica. The verifications include the following: supply temperature reset, outdoor air damper psition for relief damper/fan, and return air damper psition for relief damper/fan*.

.. sourcecode:: python

    # Get the data
    data = examples.data("example_1")

    # Loading the verification cases
    cases = cs.api.VerificationCase(json_case_path=examples.verifications("example_1"))

Here, :python:`data` is a :python:`pandas.DataFrame` which contains the timeseries for the verification, and :python:`cases` is a **ConStrain** :meth:`api.verification_case.VerificationCase` that contains all the information needed to perform a verification. To see the case information in a readable format (dictionary), run :python:`cases.case_suite`. Outside of examples, data for verifications can be directly loaded as :python:`pandas.DataFrame` and pre-processed using the functions in :meth:`api.data_processing` of **ConStrain**.

Next, we want to validate :python:`cases` by calling :meth:`api.verification_case.VerificationCase.validate` to make sure that the verification structure is correct.

.. sourcecode:: python

    cases.validate()

Then, we'll want to instantiate a verification and configure it, and run the verifications. Note that if you are using `num_thread > 1` you will need to wrap your code under the following statement `if __name__ == "__main__":`.

.. sourcecode:: python
    
    verif = cs.api.Verification(verifications=cases)
    verif.configure(output_path = "./",
                    lib_items_path = examples.library(),
                    plot_option = "all-expand",
                    fig_size = (10, 5),
                    num_threads = 1,
                    preprocessed_data = data)
    verif.run()

Finally, we can create summary report. A summary report for all verification will be created which will show the status of each verification

.. sourcecode:: python

    reporting = cs.api.Reporting(verification_json= "./*_md.json",
                                result_md_name = "report_summary.md",
                                report_format = "markdown")

    reporting.report_multiple_cases()

.. _wf:

Using **ConStrain**'s Workflows
----------------------------------

A workflow is a group of instructions that define an end-to-end verification, from data parsing and manipulation to running the verfication(s) and reporting the results. Workflows are defined using the JSON file format so once they have been established they can be re-used easily without making significant modifications. Workflows rely on **ConStrain**'s APIs.

Here is a valid workflow_. Where:

- :json:`"workflow_name"`: Name of the workflow
- :json:`"meta"`: Metadata about the workflow
- :json:`"imports"`: Python package import needed to run the workflow
- :json:`"states"`: Sequential steps to follow to perform the verification; :json:`"states"` can either be :json:`"MethodCall"` which represent a method call to one of **ConStrain**'s APIs or a :json:`"Choice"` which can be used to help define alternative steps in a workflow based on the result (referred to as payloads in a workflow).

Running a workflow can be done as follows:

.. sourcecode:: python

    import constrain as cs
    import requests, json, os
    from pathlib import Path

    # 1 - Get workflow file
    url = "https://raw.githubusercontent.com/pnnl/ConStrain/refs/heads/develop/constrain/demo/G36_demo/G36_demo_workflow.json"
    response = requests.get(url)
    data = json.loads(response.content)
    with open("G36_demo_workflow.json", "wb") as f:
        f.write(response.content)

    # 2 - Get the timeseries
    url_data = "https://raw.githubusercontent.com/pnnl/ConStrain/refs/heads/develop/constrain/demo/G36_demo/data/G36_Modelica_Jan.csv"
    response = requests.get(url_data)
    with open("./G36_Modelica_Jan.csv", "wb") as f:
        f.write(response.content)

    # 3 - Get the verification cases
    url_verification_cases = "https://raw.githubusercontent.com/pnnl/ConStrain/refs/heads/develop/constrain/demo/G36_demo/data/G36_library_verification_cases.json"
    response = requests.get(url_verification_cases)
    with open("./G36_library_verification_cases.json", "wb") as f:
        f.write(response.content)

    # 3 - Get the ConStrain library
    url_lib = "https://raw.githubusercontent.com/pnnl/ConStrain/refs/heads/develop/constrain/schema/library.json"
    response = requests.get(url_lib)
    with open("./library.json", "wb") as f:
        f.write(response.content)

    # 4 - Change data path
    data["states"]["load data"]["Parameters"]["data_path"] = str("./G36_Modelica_Jan.csv")
    data["states"]["load verification cases"]["Parameters"]["json_case_path"] = str("./G36_library_verification_cases.json")
    data["states"]["configure verification runner"]["Parameters"]["output_path"] = "./"
    data["states"]["configure verification runner"]["Parameters"]["lib_items_path"] = ("./library.json")
    data["states"]["check results"]["Parameters"][0] = "./*_md.json"
    data["states"]["reporting_object_instantiation"]["Parameters"][
        "verification_json"
    ] = "./*_md.json"

    # 3 - Run workflow
    workflow = cs.Workflow(workflow=data)
    workflow.run_workflow(verbose=True)

Interpreting Results
---------------------

After running the verifications defined above, whether it is using **ConStrain** as a library or using its Workflow capability, a `report_summary.md` file will be generated. The files contains a table that provide high-level information about the verifications that have been performed, including: case index, name of the data set, type of verification, number of samples analyzed, number of successful verifications, number of failed verifications, number of untested samples, and a general pass/fail assessement for the verification.

The markdown file contains hyperlinks so users can open a more detailed report for each verification. Detailed reports include three main sections: 1) Pass/Fail check results, 2) Result visualization, and 3) Verification case definition. The former is a repeat of what is included in the main summary report previously described. The Result visualization section shows, depending on the plotting option documented here_, one or multiple charts depicting for a specific time period or a day, the values of the different variables used by the verification and the results of the verification. The Pass / Fail flag plot shows passing verification as `1` and failing verifications as `0`. The last section provide a summary of settings used to perform the verification.

Using **ConStrain**'s Graphical User Interface (GUI)
-----------------------------------------------------

Workflow can be pretty complex and difficult to fully visualise from JSON files. **ConStrain** includes a GUI to help user create, edit, and picture workflows. If **ConStrain** has been installed, the GUI can be run by just running :bash:`constrain` in a command prompt or terminal. It is documented in this file_.

Brick Schema and **ConStrain**
--------------------------------
**ConStrain** uses the the Brick Schema to automate the verification process. For additional information, see the how-to guide_.

.. _schema: https://github.com/pnnl/ConStrain/blob/develop/constrain/schema/verification_cases.schema.json
.. _here: https://pnnl.github.io/ConStrain/Code%20Documentation.html#api.verification.Verification.configure
.. _library: https://github.com/pnnl/ConStrain/blob/develop/constrain/schema/library.json
.. _API: https://pnnl.github.io/ConStrain/Code%20Documentation.html#data-processing-py
.. _file: https://github.com/pnnl/ConStrain/blob/develop/constrain/app/README.md
.. _workflow: https://raw.githubusercontent.com/pnnl/ConStrain/refs/heads/develop/constrain/demo/G36_demo/G36_demo_workflow.json
.. _guide: https://github.com/pnnl/ConStrain/blob/develop/docs/brick_guide/brick_comment_new.md

