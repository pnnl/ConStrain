"""
Integration tests for AI Workflow UI endpoints that call backend REST APIs.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from constrain.app.ai_workflow_ui import app


client = TestClient(app)


def test_index_returns_empty_form() -> None:
    """Verify the index page loads with an empty form ready for input."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ConStrain Web UI" in response.text
    assert "Workflow Composer" in response.text
    assert 'href="/verification"' in response.text


@patch("constrain.app.ai_workflow_ui.suggest_verification_cases")
@patch("constrain.app.ai_workflow_ui.suggest_workflow")
def test_compose_endpoint_loads_form(
    mock_suggest_workflow: MagicMock, mock_suggest_cases: MagicMock
) -> None:
    """Verify the compose endpoint returns a form with prefilled context."""
    mock_suggest_workflow.return_value.data = {"type": "workflow"}
    mock_suggest_workflow.return_value.validation.issues = []
    mock_suggest_cases.return_value.data = {"type": "cases"}
    mock_suggest_cases.return_value.validation.issues = []

    response = client.post(
        "/compose",
        data={
            "goal": "Test verification",
            "data_source_annotation": "{}",
            "existing_workflow": "",
            "existing_cases": "",
            "llm_api_base": "https://example-llm.test/v1",
            "llm_model": "test-model",
            "llm_api_key": "secret-token",
            "llm_timeout": "45",
        },
    )
    assert response.status_code == 200
    assert "Test verification" in response.text
    assert "https://example-llm.test/v1" in response.text
    assert "test-model" in response.text

    workflow_call = mock_suggest_workflow.call_args
    assert workflow_call is not None
    workflow_client = workflow_call.kwargs.get("llm_client")
    assert workflow_client is not None

    cases_call = mock_suggest_cases.call_args
    assert cases_call is not None
    cases_client = cases_call.kwargs.get("llm_client")
    assert cases_client is workflow_client


@patch("constrain.app.ai_workflow_ui.suggest_verification_cases")
@patch("constrain.app.ai_workflow_ui.suggest_workflow")
def test_compose_rejects_partial_llm_form_settings(
    mock_suggest_workflow: MagicMock, mock_suggest_cases: MagicMock
) -> None:
    response = client.post(
        "/compose",
        data={
            "goal": "Test verification",
            "data_source_annotation": "{}",
            "existing_workflow": "",
            "existing_cases": "",
            "llm_api_base": "https://example-llm.test/v1",
            "llm_model": "",
        },
    )

    assert response.status_code == 200
    assert "both API base URL and model are required" in response.text
    mock_suggest_workflow.assert_not_called()
    mock_suggest_cases.assert_not_called()


@patch("constrain.app.ai_workflow_ui._api_post")
@patch("constrain.app.ai_workflow_ui._api_get")
def test_run_endpoint_uses_workflow_job_api(
    mock_api_get: MagicMock, mock_api_post: MagicMock
) -> None:
    workflow = {
        "workflow_name": "Test workflow",
        "meta": {
            "author": "Test",
            "date": "01/01/2024",
            "version": "1.0",
            "description": "Minimal valid workflow for UI integration testing",
        },
        "imports": [],
        "states": {
            "Success": {
                "Type": "MethodCall",
                "MethodCall": "print",
                "Parameters": ["ok"],
                "Start": "True",
                "End": "True",
            }
        },
    }

    mock_api_post.return_value = {"job_id": "workflow-job-1", "status": "queued"}
    mock_api_get.return_value = {
        "job_id": "workflow-job-1",
        "status": "succeeded",
        "result": {
            "success": True,
            "validation": {"valid": True, "issues": []},
            "execution": {
                "saved_to": None,
                "summary": {"steps": ["done"]},
                "error": None,
            },
        },
    }

    response = client.post(
        "/run",
        data={
            "workflow_json": json.dumps(workflow),
            "cases_json": "",
            "goal": "Run test workflow",
            "compose_debug_download_path": "/compose/debug-report/test-debug.md",
        },
    )

    assert response.status_code == 200
    assert "/compose/debug-report/test-debug.md" in response.text
    mock_api_post.assert_called_once_with(
        "/ai/workflow/jobs", {"workflow": workflow, "save_path": None}
    )
    mock_api_get.assert_called_once_with("/ai/jobs/workflow-job-1")


@patch("constrain.app.ai_workflow_ui._api_post")
def test_validate_workflow_endpoint_validates_without_running(
    mock_api_post: MagicMock,
) -> None:
    workflow = {
        "workflow_name": "Test workflow",
        "meta": {
            "author": "Test",
            "date": "01/01/2024",
            "version": "1.0",
            "description": "Manual validation test workflow",
        },
        "imports": [],
        "states": {
            "Success": {
                "Type": "MethodCall",
                "MethodCall": "print",
                "Parameters": ["ok"],
                "Start": "True",
                "End": "True",
            }
        },
    }

    response = client.post(
        "/validate-workflow",
        data={
            "workflow_json": json.dumps(workflow),
            "cases_json": "",
            "goal": "Validate test workflow",
            "compose_debug_download_path": "/compose/debug-report/test-debug.md",
        },
    )

    assert response.status_code == 200
    assert "No issues detected" in response.text
    assert "No execution requested yet." in response.text
    assert "/compose/debug-report/test-debug.md" in response.text
    mock_api_post.assert_not_called()


@patch("constrain.app.ai_workflow_ui._api_post")
def test_validate_cases_endpoint_validates_without_running(
    mock_api_post: MagicMock,
) -> None:
    workflow = {
        "workflow_name": "Test workflow",
        "meta": {
            "author": "Test",
            "date": "01/01/2024",
            "version": "1.0",
            "description": "Manual validation test workflow",
        },
        "imports": [],
        "states": {
            "Success": {
                "Type": "MethodCall",
                "MethodCall": "print",
                "Parameters": ["ok"],
                "Start": "True",
                "End": "True",
            }
        },
    }
    cases = {
        "cases": [
            {
                "name": "dummy"
            }
        ]
    }

    response = client.post(
        "/validate-cases",
        data={
            "workflow_json": json.dumps(workflow),
            "cases_json": json.dumps(cases),
            "goal": "Validate cases",
            "compose_debug_download_path": "/compose/debug-report/test-debug.md",
        },
    )

    assert response.status_code == 200
    assert "No execution requested yet." in response.text
    assert "/compose/debug-report/test-debug.md" in response.text
    mock_api_post.assert_not_called()


@patch("constrain.app.ai_workflow_ui._api_post")
@patch("constrain.app.ai_workflow_ui._api_get")
def test_verify_success_with_artifacts(
    mock_api_get: MagicMock, mock_api_post: MagicMock, tmp_path: Path
) -> None:
    """Verify POST /verify calls API and renders artifact list on success."""
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    (output_dir / "summary.md").write_text("# Summary\n")

    mock_api_post.return_value = {
        "success": True,
        "verification": {
            "case_file_path": str(output_dir / "case.json"),
            "output_dir": str(output_dir),
            "md_json_files": [str(output_dir / "1_md.json")],
        },
        "reporting": {
            "generated": True,
            "summary_path": str(output_dir / "summary.md"),
        },
    }
    mock_api_get.return_value = {
        "output_dir": str(output_dir),
        "count": 1,
        "artifacts": [
            {
                "relative_path": "summary.md",
                "size_bytes": 10,
                "modified_epoch": 1234567890,
            }
        ],
    }

    response = client.post(
        "/verify",
        data={
            "case_file_path": str(output_dir / "case.json"),
            "output_dir": str(output_dir),
            "data_file_path": "",
            "library_json_path": "",
            "plot_option": "all-compact",
            "fig_width": "6.4",
            "fig_height": "4.8",
            "tolerances_file_path": "",
            "log_level": "INFO",
            "summary_file_name": "verification_summary.md",
            "report_item_names": "",
            "generate_summary": "on",
        },
    )

    assert response.status_code == 200
    assert "Verification completed successfully" in response.text
    assert "summary.md" in response.text
    assert "10 bytes" in response.text
    mock_api_post.assert_called_once()
    assert mock_api_post.call_args_list[0].args[0] == "/ai/verification/execute"
    mock_api_get.assert_called_once_with(
        "/ai/artifacts/list",
        {"output_dir": str(output_dir), "recursive": True},
    )


@patch("constrain.app.ai_workflow_ui._api_post")
def test_verify_api_error_is_rendered(mock_api_post: MagicMock, tmp_path: Path) -> None:
    """Verify POST /verify renders API errors gracefully in HTML."""
    output_dir = tmp_path / "results"
    error_message = "Verification case file not found: /nonexistent/case.json"
    mock_api_post.side_effect = Exception(error_message)

    response = client.post(
        "/verify",
        data={
            "case_file_path": "/nonexistent/case.json",
            "output_dir": str(output_dir),
            "data_file_path": "",
            "library_json_path": "",
            "plot_option": "all-compact",
            "fig_width": "6.4",
            "fig_height": "4.8",
            "tolerances_file_path": "",
            "log_level": "INFO",
            "summary_file_name": "verification_summary.md",
            "report_item_names": "",
        },
    )

    assert response.status_code == 200
    assert error_message in response.text
    assert "execution-error" in response.text


@patch("constrain.app.ai_workflow_ui._api_post")
@patch("constrain.app.ai_workflow_ui._api_get")
def test_verify_handles_missing_artifacts(
    mock_api_get: MagicMock, mock_api_post: MagicMock, tmp_path: Path
) -> None:
    """Verify POST /verify handles case where no artifacts are present."""
    output_dir = tmp_path / "results"
    output_dir.mkdir()

    mock_api_post.return_value = {
        "success": True,
        "verification": {
            "case_file_path": str(output_dir / "case.json"),
            "output_dir": str(output_dir),
            "md_json_files": [],
        },
        "reporting": {"generated": False, "summary_path": None},
    }
    mock_api_get.return_value = {
        "output_dir": str(output_dir),
        "count": 0,
        "artifacts": [],
    }

    response = client.post(
        "/verify",
        data={
            "case_file_path": str(output_dir / "case.json"),
            "output_dir": str(output_dir),
            "data_file_path": "",
            "library_json_path": "",
            "plot_option": "all-compact",
            "fig_width": "6.4",
            "fig_height": "4.8",
            "tolerances_file_path": "",
            "log_level": "INFO",
            "summary_file_name": "verification_summary.md",
            "report_item_names": "",
        },
    )

    assert response.status_code == 200
    assert "No artifacts listed yet" in response.text


@patch("constrain.app.ai_workflow_ui._api_post")
@patch("constrain.app.ai_workflow_ui._api_get")
def test_verify_parses_report_item_names(
    mock_api_get: MagicMock, mock_api_post: MagicMock, tmp_path: Path
) -> None:
    """Verify POST /verify correctly parses comma-separated report item names."""
    output_dir = tmp_path / "results"
    output_dir.mkdir(parents=True)

    # Ensure mocks are configured to respond successfully
    mock_api_post.return_value = {
        "success": True,
        "verification": {
            "case_file_path": "",
            "output_dir": str(output_dir),
            "md_json_files": [],
        },
        "reporting": {"generated": False, "summary_path": None},
    }
    mock_api_get.return_value = {
        "output_dir": str(output_dir),
        "count": 0,
        "artifacts": [],
    }

    response = client.post(
        "/verify",
        data={
            "case_file_path": "test.json",
            "output_dir": str(output_dir),
            "data_file_path": "",
            "library_json_path": "",
            "plot_option": "all-compact",
            "fig_width": "6.4",
            "fig_height": "4.8",
            "tolerances_file_path": "",
            "log_level": "INFO",
            "summary_file_name": "verification_summary.md",
            "report_item_names": "G36FreezeProtectionStage1, G36FreezeProtectionStage2, G36SupplyAirTemperatureSetpoint",
        },
    )

    # Verify the response is successful
    assert response.status_code == 200

    # Verify _api_post was called with the correct report_item_names
    assert mock_api_post.called, "_api_post should have been called"
    call_args = mock_api_post.call_args
    payload = call_args.args[1]  # Get the payload argument (second positional arg)
    expected_items = [
        "G36FreezeProtectionStage1",
        "G36FreezeProtectionStage2",
        "G36SupplyAirTemperatureSetpoint",
    ]
    assert payload["report_item_names"] == expected_items


def test_artifact_download_redirect() -> None:
    """Verify /artifact/download redirects to the backend API endpoint."""
    with patch.dict(
        "os.environ", {"CONSTRAIN_PUBLIC_API_BASE_URL": "http://localhost:8000"}
    ):
        response = client.get(
            "/artifact/download",
            params={"output_dir": "/results", "relative_path": "file.md"},
            follow_redirects=False,
        )

    assert response.status_code == 307
    assert response.headers["location"].startswith(
        "http://localhost:8000/ai/artifacts/download"
    )
    assert "output_dir=%2Fresults" in response.headers["location"]
    assert "relative_path=file.md" in response.headers["location"]


def test_artifact_download_zip_redirect() -> None:
    """Verify /artifact/download-zip redirects to the backend API endpoint."""
    with patch.dict(
        "os.environ", {"CONSTRAIN_PUBLIC_API_BASE_URL": "http://localhost:8000"}
    ):
        response = client.get(
            "/artifact/download-zip",
            params={"output_dir": "/results"},
            follow_redirects=False,
        )

    assert response.status_code == 307
    assert response.headers["location"].startswith(
        "http://localhost:8000/ai/artifacts/download-zip"
    )
    assert "output_dir=%2Fresults" in response.headers["location"]
