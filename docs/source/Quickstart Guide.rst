Quickstart Guide
=================

.. role:: python(code)
   :language: python
.. role:: json(code)
   :language: JSON
.. role:: bash(code)
   :language: bash

This guide provides a quick overview of how to get started with **ConStrain**. Verifications of building system control related timeseries using **ConStrain** can either be done by using **ConStrain** as a Python library or by using a **ConStrain** workflow.

Installing **ConStrain**
-------------------------
**ConStrain** can be installed from PyPI by running the following command.

.. sourcecode:: bash

   pip install constrain

Using **ConStrain** as a library
---------------------------------

First, let's import the package.

.. sourcecode:: python

    import constrain as cs

**ConStrain** includes an :python:`Examples` module which contains sample data and examples of verifications. Information about eac example can be obtained by running the following command. A dictionary is returned which shows information about each example. 

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

Then, we'll want to instantiate a verification and configure it, and run the verifications.

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

Using **ConStrain** workflows
------------------------------

A workflow is a group of instructions that define an end-to-end verification, from data parsing and manipulation to running the verfication(s) and reporting the results. Workflows are defined using the JSON file format so once they have been established they can be re-used easily without making significant modifications. Workflows rely on **ConStrain**'s APIs.

Below is shown a valid workflow. Let's look at its structure.

- :json:`"workflow_name"`: Name of the workflow
- :json:`"meta"`: Metadata about the workflow
- :json:`"imports"`: Python package import needed to run the workflow
- :json:`"states"`: Sequential steps to follow to perform the verification; :json:`"states"` can either be :json:`"MethodCall"` which represent a method call to one of **ConStrain**'s APIs or a :json:`"Choice"` which can be used to help define alternative steps in a workflow based on the result (referred to as payloads in a workflow).

.. sourcecode:: JSON

    {
      "workflow_name": "G36 Demo workflow",
      "meta": {
        "author": "ConStrain Team",
        "date": "06/29/2023",
        "version": "1.0",
        "description": "Demo workflow to showcase G36 verification item development"
      },
      "imports": [
        "numpy as np",
        "pandas as pd"
      ],
      "states": {
        "load data": {
          "Type": "MethodCall",
          "MethodCall": "DataProcessing",
          "Parameters": {
            "data_path": "./demo/G36_demo/data/G36_Modelica_Jan.csv",
            "data_source": "EnergyPlus"
          },
          "Payloads": {
            "data_processing_obj": "$",
            "data": "$.data"
          },
          "Start": "True",
          "Next": "load verification cases"
        },
        "load verification cases": {
          "Type": "MethodCall",
          "MethodCall": "VerificationCase",
          "Parameters": {
            "json_case_path": "./demo/G36_demo/data/G36_library_verification_cases.json"
          },
          "Payloads": {
            "verification_case_obj": "$",
            "original_case_keys": "$.case_suite.keys()"
          },
          "Next": "check original case length"
        },
        "check original case length": {
          "Type": "Choice",
          "Choices": [
            {
              "Value": "len(Payloads['original_case_keys']) == 3",
              "Equals": "True",
              "Next": "validate cases"
            }
          ],
          "Default": "Report Error in workflow"
        },
        "validate cases": {
          "Type": "Choice",
          "Choices": [
            {
              "Value": "Payloads['verification_case_obj'].validate()",
              "Equals": "True",
              "Next": "setup verification"
            }
          ],
          "Default": "Report Error in workflow"
        },
        "setup verification": {
          "Type": "MethodCall",
          "MethodCall": "Verification",
          "Parameters": {
            "verifications": "Payloads['verification_case_obj']"
          },
          "Payloads": {
            "verification_obj": "$"
          },
          "Next": "configure verification runner"
        },
        "configure verification runner": {
          "Type": "MethodCall",
          "MethodCall": "Payloads['verification_obj'].configure",
          "Parameters": {
            "output_path": "./demo/G36_demo",
            "lib_items_path": "./schema/library.json",
            "plot_option": "+x None",
            "fig_size": "+x (6, 5)",
            "num_threads": 1,
            "preprocessed_data": "Payloads['data']"
          },
          "Payloads": {},
          "Next": "run verification"
        },
        "run verification": {
          "Type": "MethodCall",
          "MethodCall": "Payloads['verification_obj'].run",
          "Parameters": {},
          "Payloads": {
            "verification_return": "$"
          },
          "Next": "check results"
        },
        "check results": {
          "Type": "MethodCall",
          "MethodCall": "glob.glob",
          "Parameters": [
            "./demo/G36_demo/*_md.json"
          ],
          "Payloads": {
            "length_of_mdjson": "len($)"
          },
          "Next": "check number of result files"
        },
        "check number of result files": {
          "Type": "Choice",
          "Choices": [
            {
              "Value": "Payloads['length_of_mdjson']",
              "Equals": "3",
              "Next": "reporting_object_instantiation"
            }
          ],
          "Default": "Report Error in workflow"
        },
        "reporting_object_instantiation": {
          "Type": "MethodCall",
          "MethodCall": "Reporting",
          "Parameters": {
            "verification_json": "./demo/G36_demo/*_md.json",
            "result_md_name": "report_summary.md",
            "report_format": "markdown"
          },
          "Payloads": {
            "reporting_obj": "$"
          },
          "Next": "report_cases"
        },
        "report_cases": {
          "Type": "MethodCall",
          "MethodCall": "Payloads['reporting_obj'].report_multiple_cases",
          "Parameters": {},
          "Payloads": {},
          "Next": "Success"
        },
        "Success": {
          "Type": "MethodCall",
          "MethodCall": "print",
          "Parameters": [
            "Congratulations! the demo workflow is executed with expected results and no error!"
          ],
          "End": "True"
        },
        "Report Error in workflow": {
          "Type": "MethodCall",
          "MethodCall": "logging.error",
          "Parameters": [
            "Something is wrong in the workflow execution"
          ],
          "End": "True"
        }
      }
    }

Running a workflow can be done as follows.

.. sourcecode:: python

    import constrain as cs

    workflow_file = "./demo/G36_demo/G36_demo_workflow.json"
    workflow = cs.Workflow(workflow=workflow_file)
    workflow.run_workflow(verbose=True)

Using **ConStrain**'s graphical user interface (GUI)
-----------------------------------------------------

Workflow can be pretty complex and difficult to fully visualise from JSON files. **ConStrain** includes a GUI to help user create, edit, and picture workflows. If **ConStrain** has been installed, the GUI can be run by just running :bash:`constrain` in a command prompt or terminal.
