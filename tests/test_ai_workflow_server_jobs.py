import time
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import constrain.app.ai_workflow_server as server_mod
from constrain.app.ai_workflow_server import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_job_store() -> None:
    with server_mod._job_store_lock:
        server_mod._job_store.clear()


def _wait_for_job(job_id: str, timeout: float = 2.0) -> dict:
    deadline = time.time() + timeout
    last_payload = None
    while time.time() < deadline:
        response = client.get(f"/ai/jobs/{job_id}")
        assert response.status_code == 200
        last_payload = response.json()
        if last_payload["status"] in {"succeeded", "failed"}:
            return last_payload
        time.sleep(0.01)
    raise AssertionError(
        f"Job {job_id} did not finish in time. Last payload: {last_payload}"
    )


@patch("constrain.app.ai_workflow_server._run_workflow_execution")
def test_submit_workflow_job_returns_succeeded_result(
    mock_run_workflow_execution,
) -> None:
    mock_run_workflow_execution.return_value = {
        "success": True,
        "validation": {"valid": True, "issues": []},
        "execution": {"saved_to": None, "summary": {"steps": 1}, "error": None},
    }

    response = client.post(
        "/ai/workflow/jobs", json={"workflow": {"steps": []}, "save_path": None}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["job_type"] == "workflow"
    assert payload["status"] == "queued"

    finished = _wait_for_job(payload["job_id"])
    assert finished["status"] == "succeeded"
    assert finished["result"]["success"] is True
    assert finished["error"] is None


@patch("constrain.app.ai_workflow_server._run_verification_execution")
def test_submit_verification_job_records_failure(
    mock_run_verification_execution,
) -> None:
    mock_run_verification_execution.side_effect = HTTPException(
        status_code=400,
        detail="Verification case file not found: /missing.json",
    )

    response = client.post(
        "/ai/verification/jobs",
        json={
            "case_file_path": "/missing.json",
            "output_dir": "/tmp/results",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["job_type"] == "verification"

    finished = _wait_for_job(payload["job_id"])
    assert finished["status"] == "failed"
    assert finished["result"] is None
    assert finished["error"]["status_code"] == 400
    assert "Verification case file not found" in finished["error"]["detail"]


def test_get_job_returns_404_for_unknown_id() -> None:
    response = client.get("/ai/jobs/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found: does-not-exist"
