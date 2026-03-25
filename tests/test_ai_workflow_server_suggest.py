from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from constrain.app.ai_workflow_server import app


client = TestClient(app)


def _composer_result(payload_key: str) -> SimpleNamespace:
    return SimpleNamespace(
        ok=True,
        data={payload_key: {"name": "example"}},
        validation=SimpleNamespace(valid=True, issues=[]),
        raw_text="{}",
    )


@patch("constrain.app.ai_workflow_server.suggest_workflow")
@patch("constrain.app.ai_workflow_server.get_default_llm_client")
def test_workflow_suggest_accepts_request_llm_settings(
    mock_get_default_llm_client,
    mock_suggest_workflow,
) -> None:
    mock_get_default_llm_client.return_value = None
    mock_suggest_workflow.return_value = _composer_result("workflow")

    response = client.post(
        "/ai/workflow/suggest",
        json={
            "goal_description": "Build a workflow",
            "llm_settings": {
                "api_base": "https://example-llm.test/v1",
                "model": "test-model",
                "api_key": "secret-token",
                "timeout": 45,
            },
        },
    )

    assert response.status_code == 200
    call = mock_suggest_workflow.call_args
    assert call is not None
    llm_client = call.kwargs.get("llm_client")
    assert llm_client is not None
    assert llm_client.config.api_base == "https://example-llm.test/v1"
    assert llm_client.config.model == "test-model"
    assert llm_client.config.api_key == "secret-token"
    assert llm_client.config.timeout == 45


@patch("constrain.app.ai_workflow_server.suggest_verification_cases")
@patch("constrain.app.ai_workflow_server.get_default_llm_client")
def test_cases_suggest_accepts_request_llm_settings(
    mock_get_default_llm_client,
    mock_suggest_cases,
) -> None:
    mock_get_default_llm_client.return_value = None
    mock_suggest_cases.return_value = _composer_result("cases")

    response = client.post(
        "/ai/cases/suggest",
        json={
            "goal_description": "Build case suite",
            "llm_settings": {
                "api_base": "https://example-llm.test/v1",
                "model": "test-model",
            },
        },
    )

    assert response.status_code == 200
    call = mock_suggest_cases.call_args
    assert call is not None
    llm_client = call.kwargs.get("llm_client")
    assert llm_client is not None
    assert llm_client.config.api_base == "https://example-llm.test/v1"
    assert llm_client.config.model == "test-model"


def test_workflow_suggest_rejects_partial_llm_settings() -> None:
    response = client.post(
        "/ai/workflow/suggest",
        json={
            "goal_description": "Build a workflow",
            "llm_settings": {
                "api_base": "https://example-llm.test/v1",
            },
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "When llm_settings is provided, both api_base and model are required."
    )


@patch("constrain.app.ai_workflow_server.get_default_llm_client")
def test_workflow_suggest_keeps_existing_env_fallback(mock_get_default_llm_client) -> None:
    mock_get_default_llm_client.return_value = None

    response = client.post(
        "/ai/workflow/suggest",
        json={
            "goal_description": "Build a workflow",
        },
    )

    assert response.status_code == 503
    assert "No LLM client configured" in response.json()["detail"]
