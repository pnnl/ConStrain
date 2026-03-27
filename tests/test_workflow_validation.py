import json
from pathlib import Path

from constrain.ai.schema_utils import validate_workflow_dict
from constrain.api.workflow import Choice, Workflow


def _load_valid_workflow() -> dict:
    workflow_path = (
        Path(__file__).resolve().parents[1] / "tests" / "api" / "data" / "testworkflow.json"
    )
    with workflow_path.open("r", encoding="utf-8") as workflow_file:
        return json.load(workflow_file)


def test_validate_workflow_dict_ignores_working_dir_side_effects(monkeypatch):
    workflow = _load_valid_workflow()
    workflow["working_dir"] = "g36_jan_verification"

    def fail_if_called(*args, **kwargs):
        raise AssertionError("validation should not attempt to create a working directory")

    monkeypatch.setattr("pathlib.Path.mkdir", fail_if_called)

    result = validate_workflow_dict(workflow)

    assert all(
        issue.validator != "WorkflowEngine.validate"
        or not issue.message.startswith("Exception during Workflow validation:")
        for issue in result.issues
    )


def test_change_work_dir_handles_permission_error_without_winerror(monkeypatch):
    workflow = _load_valid_workflow()
    workflow["working_dir"] = "g36_jan_verification"

    monkeypatch.setattr("constrain.api.workflow.os.path.exists", lambda _: False)

    def raise_permission_error(*args, **kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr("pathlib.Path.mkdir", raise_permission_error)

    engine = Workflow.create_workflow_engine(workflow)

    assert engine is not None


def test_choice_all_uses_documented_all_array():
    next_state = Choice(
        {
            "Choices": [
                {
                    "ALL": [
                        {"Value": "Payloads['x']", "Equals": "True", "Next": "done"},
                        {"Value": "Payloads['y']", "Equals": "True", "Next": "done"},
                    ],
                    "Next": "done",
                }
            ],
            "Default": "fallback",
        },
        {"x": True, "y": True},
    ).check_choices()

    assert next_state == "done"
