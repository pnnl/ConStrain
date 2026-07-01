from unittest.mock import patch

from constrain.ai.workflow_composer import _build_workflow_system_prompt


@patch("constrain.ai.workflow_composer.list_verification_classes")
@patch("constrain.ai.workflow_composer.list_workflow_callables")
@patch("constrain.ai.workflow_composer._load_workflow_reference_markdown")
def test_workflow_prompt_includes_reference_markdown(
    mock_load_reference,
    mock_list_callables,
    mock_list_verification_classes,
) -> None:
    reference_text = "# Workflow reference\nUse this rule."
    mock_load_reference.return_value = reference_text
    mock_list_callables.return_value = []
    mock_list_verification_classes.return_value = []

    prompt = _build_workflow_system_prompt()

    assert "---BEGIN WORKFLOW REFERENCE---" in prompt
    assert reference_text in prompt
    assert "---END WORKFLOW REFERENCE---" in prompt
