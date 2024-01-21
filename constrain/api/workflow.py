"""
workflow.py
====================================
Workflow API
"""

import glob
import sys, logging, json, os, datetime
from typing import Union

sys.path.append("./constrain")
sys.path.append("..")
from constrain.api import (
    BrickCompliance,
    VerificationLibrary,
    DataProcessing,
    VerificationCase,
    Verification,
    Reporting,
)


# helper
def timenow():
    return datetime.datetime.now()


def strnow():
    return timenow().strftime("%H:%M:%S")


class WorkflowEngine:
    def __init__(self, workflow, run_workflow_now=False):
        self.end_state_name = None
        self.start_state_name = None
        self.payloads = {}
        self.states = {}
        self.workflow_dict = {}
        self.running_sequence = []

        # checking workflow validity is handed over to the API method.
        if isinstance(workflow, str):
            self.load_workflow_json(workflow)

        if isinstance(workflow, dict):
            self.workflow_dict = workflow

        self.load_states()

        if run_workflow_now:
            self.run_workflow()

    def validate(self, verbose: bool = False) -> bool:
        """function to be implemented to check for high level validity of the workflow definition"""
        workflow_schema = {
            "workflow_name": str,
            "meta": {"author": str, "date": str, "version": str, "description": str},
            "imports": list,
            "states": {"*": dict},
        }

        def _validate_workflow(schema, instance, verbose) -> bool:
            # TODO: JXL this is duplicate from VerificationCase.validate_verification_case_structure._validate_case_structure_helper. Refactor needed.
            for schema_key, schema_value in schema.items():
                # accommodate data points alike scenarios (random string key with required value structure)
                if schema_key == "*":
                    keys = list(instance.keys())
                else:
                    keys = [schema_key]

                for key in keys:
                    # check key match
                    if key not in instance:
                        logging.error(f"Missing required key '{key}' in {instance}")
                        return False

                    case_value = instance[key]

                    if isinstance(schema_value, dict):
                        # recursively check nested value
                        is_cases_valid = _validate_workflow(
                            schema_value, case_value, verbose
                        )
                        if not is_cases_valid:
                            return False
                    else:
                        # check leaf value match
                        # if require float, it can be int
                        if schema_value == float:
                            eligible_types = [int, float]
                        else:
                            eligible_types = [schema_value]

                        type_match_list = [
                            isinstance(case_value, sv) for sv in eligible_types
                        ]

                        if not any(type_match_list):
                            logging.error(
                                f"The type of '{key}' key must be {schema_value}, but {type(case_value)} is provided."
                            )
                            return False
                        else:
                            if verbose:
                                print(
                                    f"The type of {key} has the correct type {schema_value}"
                                )
            return True

        return _validate_workflow(workflow_schema, self.workflow_dict, verbose)

    def import_package(self) -> None:
        """Import third party packages based on the "imports" element values of the workflow json.
        E.g.: {
        ...
        "imports": [
            "numpy as np",
            "pandas as pd",
            "datetime"
        ],
        ...
        }
        """
        import_list = []
        if "imports" in self.workflow_dict:
            import_list = self.workflow_dict["imports"]
        for line in import_list:
            cp = line
            if " as " in line:
                cp = line.split(" as ")[-1]
            exec(f"import {line}", globals())

    def load_workflow_json(self, workflow_path: str) -> None:
        """Load workflow from a json workflow definition.

        Args:
            workflow_path (str): path to the workflow json file.
        """
        with open(workflow_path) as f:
            self.workflow_dict = json.load(f)

    def load_states(self) -> None:
        """load states from the workflow definition with some sanity checks."""
        for state_name, state_dict in self.workflow_dict["states"].items():
            # there should be no duplicate names
            if state_name in self.states:
                logging.error(
                    f"State name [{state_name}] is not unique in the loaded workflow. This is NOT allowed."
                )
                return None

            self.states[state_name] = state_dict
            if "Start" in state_dict and state_dict["Start"] == "True":
                self.start_state_name = state_name

            if "End" in state_dict and state_dict["End"] == "True":
                self.end_state_name = state_name
                continue

            if (state_dict["Type"] != "Choice") and ("Next" not in state_dict):
                logging.error(
                    f"Non-Choice state [{state_name} is not an End state and it has no Next state. This is NOT allowed."
                )

    def run_state(self, state_name: str) -> Union[None, str]:
        """Run a specific states by state_name. This is not a external facing method and is only supposed to be called by run_workflow.

        Args:
            state_name (str): name of the state to execute.

        Returns:
            Union[None, str]: name of the next state to run or None if there is no next state.
        """
        state_dict = self.states[state_name]
        state_type = state_dict["Type"]
        next_state = None

        if state_type == "MethodCall":
            self.payloads = MethodCall(state_dict, self.payloads).run().get_payloads()
            if "Next" in state_dict:
                next_state = state_dict["Next"]

        if state_type == "Choice":
            next_state = Choice(state_dict, self.payloads).check_choices()

        if (state_name != self.end_state_name) and (next_state is not None):
            return next_state
        else:
            return None

    def run_workflow(self, verbose=True, max_states: int = 1000) -> None:
        """Workflow runner with a maximum steps allowed setting.

        Args:
            max_states (int, optional): Maximum number of states to run allowed. Defaults to 1000.
        """
        start_time = timenow()
        print(f"Start running workflow at {start_time.strftime('%H:%M:%S')}")

        if verbose:
            print(f"Importing packages specified in workflow -- [{strnow()}]")
        self.import_package()
        current_state_name = self.start_state_name

        if verbose:
            print(
                f"Start running workflow with start state [{self.start_state_name}] with maximum allowable number of states being [{max_states}] -- [{strnow()}]"
            )

        state_count = 0
        touch_limit = False
        while current_state_name is not None:
            state_count += 1

            if verbose:
                print(
                    f"Running state {state_count}: [{current_state_name}] ...", end=" "
                )

            self.running_sequence.append(current_state_name)
            current_state_name = self.run_state(current_state_name)

            if verbose:
                print(f"Done. -- [{strnow()}]")

            if state_count > max_states:
                e_msg = (
                    "Reaching maximum allowable number of states. Workflow terminated."
                )
                if verbose:
                    print(e_msg)
                touch_limit = True
                logging.warning(
                    "Reaching maximum allowable number of states. Workflow terminated."
                )
                break

        end_time = timenow()
        duration = end_time - start_time
        print(
            f"Workflow done at {end_time.strftime('%H:%M:%S')}, a total of {state_count} states were executed in {duration}."
        )

    def summarize_workflow_run(self) -> dict:
        """Summarize the states running sequence after a workflow is executed.

        Returns:
            dict: a summary dictionary with two keys: `total_states_executed` and `state_running_sequence`.
        """
        print(
            f"A total of {len(self.running_sequence)} states were executed with the following sequence:"
        )
        step_count = 0
        for element in self.running_sequence:
            step_count += 1
            print(f"State {step_count}: {element}")

        return {
            "total_states_executed": step_count,
            "state_running_sequence": self.running_sequence,
        }


class Workflow:
    def __init__(self, workflow: Union[str, dict] = None):
        """Instantiate a Workflow class object and load specified workflow as a `dict` in `self.workflow`

        Args:
            workflow (Union[str, dict], optional): str path to the workflow definition json file or dict of the actual workflow definition. Defaults to None.
        """
        self.workflow_engine = None

        if workflow is None:
            logging.warning(
                "Workflow is not provided at time of initialization. self.workflow_engine is set to None. Workflow can be added later by calling self.load_workflow(workflow)"
            )
        else:
            self.load_workflow(workflow)

    def load_workflow(self, workflow: Union[str, dict]) -> None:
        """Load workflow definition from a json file or dict to `self.workflow`.

        Args:
            workflow (Union[str, dict]): str path to the workflow definition json file or dict of the actual workflow definition.
        """
        if self.workflow_engine is not None:
            logging.warning(
                "self.workflow_engine is not None, load_workflow will overwrite it with a new workflow."
            )
        self.workflow_engine = self.create_workflow_engine(workflow)

    @staticmethod
    def create_workflow_engine(
        workflow: Union[str, dict]
    ) -> Union[None, WorkflowEngine]:
        """Instantiate a WorkflowEngine object with specified workflow definition.

        Args:
            workflow (Union[str, dict]): str path to the workflow definition json file or dict of the actual workflow definition. Defaults to None.

        Returns:
            Union[None, WorkflowEngine]: Instantiated WorkflowEngine object if provided workflow is valid; None otherwise.
        """
        if (isinstance(workflow, str) and os.path.isfile(workflow)) or isinstance(
            workflow, dict
        ):
            workflow_engine = WorkflowEngine(workflow)
        else:
            logging.error(
                "workflow needs to be either a str path to the workflow json file or a dict of the workflow definition."
            )
            workflow_engine = None
        return workflow_engine

    @staticmethod
    def list_existing_workflows(workflow_dir: str = None) -> Union[dict, None]:
        """List existing workflows (defined as json files) under a specific directory path.

        Args:
            workflow_dir (str, optional): path to the directory containing workflow definitions (including sub directories). By default, point to the path of the example folder. @JXL TODO example folder to be specified

        Returns:
            Union[dict, None]: `dict` with keys being workflow names and values being a `Dict` with the following keys:
                - `workflow_json_path`: path to the file of the workflow
                - `workflow`: `Dict` of the workflow, loaded from the workflow json definition
        """
        if isinstance(workflow_dir, str) and os.path.isfile(workflow_dir):
            if workflow_dir[-1] != "/":
                workflow_dir = workflow_dir + "/"
            found_files = glob.glob(f"{workflow_dir}**/*.json", recursive=True)
        else:
            logging.error(
                "workflow_dir needs to point to a valid path containing potential workflow json files."
            )
            return None

        num_found_files = len(found_files)

        if num_found_files == 0:
            logging.warning(f"There is no json file in {workflow_dir}")
            return None

        workflows = {}
        for json_file_path in found_files:
            temp_wfe = WorkflowEngine(json_file_path)
            if temp_wfe.validate():
                workflows[temp_wfe.workflow_dict["workflow_name"]] = {
                    "workflow_json_path": json_file_path,
                    "workflow": temp_wfe.workflow_dict,
                }

    @staticmethod
    def validate_workflow_definition(workflow: Union[str, dict], verbose=False) -> dict:
        """Validate a workflow definition.

        Args:
            workflow (Union[str, dict]): If str, this is assumed to be the path to the workflow definition json file; If dict, this is assumed to be loaded from the workflow json definition.
            verbose (bool, optional): Verbose output for validate. Defaults to False.

        Returns:
            dict: `dict` with the following keys:
                - `workflow_validity`: bool flag of the validity of the workflow definition
                - `detail`: detailed info about the validity check.
        """

        temp_workflow_engine = Workflow.create_workflow_engine(workflow)
        return temp_workflow_engine.validate()

    def validate(self, verbose=False) -> dict:
        """Validate `self.workflow`

        Args:
            verbose (bool, optional): Verbose output for validate. Defaults to False.

        Returns:
            dict: `dict` with the following keys:
                - `workflow_validity`: bool flag of the validity of the workflow definition
                - `detail`: detailed info about the validity check.
        """
        return self.workflow_engine.validate()

    def save(self, json_path: str = None) -> None:
        """Save the workflow as a json file.

        Args:
            json_path (str, optional): path to the file to be saved. Defaults to None.
        """

        if self.workflow_engine is None:
            logging.warning("self.workflow_engine is None, there is nothing to save.")
        else:
            if isinstance(json_path, str):
                self.workflow_engine.save_workflow(json_path)
            else:
                logging.error("json_path needs to be str")

    def run_workflow(self, verbose: bool = False) -> bool:
        """Execute the workflow defined in self.workflow

        Args:
            verbose (bool, optional): bool. Wether to output detailed information. Defaults to False.

        Returns:
            bool: Whether the run is successful or not.

        """
        self.workflow_engine.run_workflow(verbose)


class MethodCall:
    """The MethodCall State class. This class also covers the `Embedded MethodCall` state type.
    A typical use case of execute a MethodCall state would be: `self.payloads = MethodCall(state_dict, self.payloads).run().get_payloads()`
    """

    def __init__(self, state_dict, payloads):
        self.payloads = payloads  # self.payloads takes in the input payloads, add key-value pairs contents based on state_dict['Payloads'], and will be available by self.get_payloads()
        self.parameters = {}
        self.state_dict = state_dict
        self.dollar = None  # the return of the current method call will be stored in this variable.
        self.build_parameters(state_dict)

    def build_parameters(self, state_dict):
        if isinstance(state_dict["Parameters"], dict):
            for k, v in state_dict["Parameters"].items():
                self.parameters[k] = self.build_param_value(v)
        if isinstance(state_dict["Parameters"], list):
            # some python built-in methods only accept positional arguments
            self.parameters = [
                self.build_param_value(x) for x in state_dict["Parameters"]
            ]

    def build_param_value(self, v):
        if isinstance(v, dict):
            # if parameter value is a dict, then it needs to be an embedded method call style
            new_v = self.embedded_call(v)
            return new_v

        if isinstance(v, int) or isinstance(v, float):
            return v

        if isinstance(v, str):
            # special string treatment
            Payloads = (
                self.payloads
            )  # to be used by "...Payloads['xxx']... in parameter value" TODO:JXL to be tested.
            if v.split("[")[0] == "Payloads":
                # only in this case we eval
                return eval(v)
            elif v[:3] == "+x ":  # unique prefix for evaluate the rest of the string
                return eval(v[3:])
            else:
                # in all other string param value, we consider it is a string. This is for clarity and security. More complicated parameter should use embedded methodcall
                return v

    def run(self):
        Payloads = (
            self.payloads
        )  # to be used by "...Payloads['xxx']... in self.state_dict["MethodCall"]"
        method_call = eval(self.state_dict["MethodCall"])
        # TODO JXL: handle non-method calls, maybe just (self.dollar = method_call)? Need tests
        if isinstance(self.parameters, dict):
            self.dollar = method_call(**self.parameters)
        if isinstance(self.parameters, list):
            self.dollar = method_call(*self.parameters)
        return self

    def get_method_return(self):
        return self.dollar

    def get_payloads(self):
        Payloads = self.payloads
        if "Payloads" in self.state_dict:
            for k, v in self.state_dict["Payloads"].items():
                if isinstance(v, str):
                    # only eval if v is string
                    self.payloads[k] = eval(v.replace("$", "self.dollar"))
                else:
                    self.payloads[k] = v
        return self.payloads

    def embedded_call(self, embedded_case_dict):
        if embedded_case_dict["Type"] != "Embedded MethodCall":
            logging.error(
                f"If parameter value is a dict, it needs to be of type 'Embedded MethodCall'. Problematic state definition: {embedded_case_dict}"
            )
            return None

        return MethodCall(embedded_case_dict, self.payloads).run().get_method_return()


class Choice:
    """The Choice state that check conditions to decide next step.
    A typical use case of execute a Choice state would be: `next_state = Choice(state_dict, self.payloads).check_choices()`
    """

    def __init__(self, state_dict, payloads):
        self.payloads = payloads
        self.state_dict = state_dict

    def check_choices(self):
        for choice in self.state_dict["Choices"]:
            choice_return = self.check_choice(choice)
            if isinstance(choice_return, str):
                return choice_return
            # if current choice does not give a next step, then check the next one
            continue

        # no valid next step has been identified. check if there is a default state, if not, log error
        if "Default" in self.state_dict:
            return self.state_dict["Default"]
        else:
            logging.error("Among all choices, no valid next step identified. Abort!")
            return None

    def check_choice(self, choice):
        if not isinstance(choice, dict):
            logging.error("choice has to be a dict")
            return None
        if "Value" not in choice:
            # when 'Value' is not in choice, a logical expression key is expected
            # check only one logic expression in the key
            eligible_logic = ["ALL", "ANY", "NONE"]
            keycheck_flag = [(ek in choice) for ek in eligible_logic]
            if sum(keycheck_flag) != 1:
                logging.error(
                    "For logical expression choices state, there needs to be exactly one key of either 'ALL', or 'ANY', or 'NONE'."
                )
                return None

            if "ALL" in choice:
                flag_list = [self.get_choice_value(x) for x in choice["AND"]]
                choice_value = all(flag_list)
            if "NONE" in choice:
                flag_list = [self.get_choice_value(x) for x in choice["NONE"]]
                choice_value = not any(flag_list)
            if "ANY" in choice:
                choice_value = False
                for subchoice in choice["ANY"]:
                    if self.get_choice_value(subchoice):
                        choice_value = True
                        break

        else:
            # 'leaf' choice implementation
            choice_value = self.get_choice_value(choice)

        if choice_value:
            return choice["Next"]
        else:
            return False

    def get_choice_value(self, choice):
        Payloads = self.payloads  # to be used by "...Payloads['xxx']... in choice dict"
        left = choice["Value"]
        right = choice["Equals"]

        # only eval when it is a string
        if isinstance(left, str):
            left = eval(choice["Value"])
        if isinstance(right, str):
            right = eval(choice["Equals"])

        if left == right:
            return True
        else:
            return False


def main():
    WorkflowEngine("./tests/api/data/testworkflow.json")


if __name__ == "__main__":
    main()
