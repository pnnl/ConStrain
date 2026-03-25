"""
FastAPI app exposing AI-assisted workflow and verification-case composer endpoints.

Endpoints (paths are intentionally simple and versionless for now):

- POST /ai/workflow/suggest
- POST /ai/cases/suggest
- POST /ai/workflow/validate
- POST /ai/cases/validate
- GET  /ai/catalog
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import glob
import io
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Literal, Optional
import time
import uuid
import zipfile

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from constrain.api import DataProcessing, Reporting, Verification, VerificationCase
from constrain.ai import (
    get_default_llm_client,
)
from constrain.ai.introspection import (
    as_serializable,
    list_verification_classes,
    list_workflow_callables,
)
from constrain.ai.schema_utils import (
    validate_case_suite_dict,
    validate_workflow_dict,
)
from constrain.ai.workflow_composer import (
    ComposerResult,
    suggest_verification_cases,
    suggest_workflow,
)
from constrain.ai.workflow_runner import run_workflow_from_dict


app = FastAPI(title="ConStrain AI Workflow Composer")


_job_executor = ThreadPoolExecutor(max_workers=4)
_job_store_lock = Lock()
_job_store: Dict[str, Dict[str, Any]] = {}


class WorkflowSuggestRequest(BaseModel):
    goal_description: str
    data_context: Optional[Dict[str, Any]] = None
    existing_workflow: Optional[Dict[str, Any]] = None
    cases_context: Optional[Dict[str, Any]] = None


class CasesSuggestRequest(BaseModel):
    goal_description: str
    signals_available: Optional[Dict[str, Any]] = None
    existing_cases: Optional[Dict[str, Any]] = None


class ValidateWorkflowRequest(BaseModel):
    workflow: Dict[str, Any]


class ValidateCasesRequest(BaseModel):
    cases: Dict[str, Any]


class ExecuteWorkflowRequest(BaseModel):
    workflow: Dict[str, Any]
    save_path: Optional[str] = None


class ExecuteVerificationRequest(BaseModel):
    case_file_path: str
    output_dir: str
    data_file_path: Optional[str] = None
    data_source: str = "EnergyPlus"
    library_json_path: Optional[str] = None
    plot_option: str = "all-compact"
    fig_size: List[float] = [6.4, 4.8]
    tolerances_file_path: Optional[str] = None
    log_level: str = "INFO"
    generate_summary: bool = True
    summary_file_name: str = "verification_summary.md"
    report_item_names: Optional[List[str]] = None


class JobStatusResponse(BaseModel):
    job_id: str
    job_type: Literal["workflow", "verification"]
    status: Literal["queued", "running", "succeeded", "failed"]
    created_at_epoch: float
    started_at_epoch: Optional[float] = None
    finished_at_epoch: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Any] = None


def _ensure_llm_available() -> None:
    if get_default_llm_client() is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "No LLM client configured. Set CONSTRAIN_LLM_API_BASE and "
                "CONSTRAIN_LLM_MODEL (and optionally CONSTRAIN_LLM_API_KEY) "
                "in the environment."
            ),
        )


def _resolve_output_dir(output_dir: str) -> Path:
    output_dir_path = Path(output_dir).expanduser().resolve()
    if not output_dir_path.exists() or not output_dir_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Output directory not found: {output_dir_path}",
        )
    return output_dir_path


def _resolve_artifact_path(output_dir_path: Path, relative_path: str) -> Path:
    artifact_path = (output_dir_path / relative_path).resolve()
    if artifact_path == output_dir_path or output_dir_path not in artifact_path.parents:
        raise HTTPException(status_code=400, detail="Invalid artifact path.")
    if not artifact_path.exists() or not artifact_path.is_file():
        raise HTTPException(
            status_code=404, detail=f"Artifact not found: {relative_path}"
        )
    return artifact_path


def _serialize_validation_issues(issues: List[Any]) -> List[Dict[str, Any]]:
    return [
        {
            "loc": issue.loc,
            "message": issue.message,
            "validator": issue.validator,
        }
        for issue in issues
    ]


def _get_job(job_id: str) -> Dict[str, Any]:
    with _job_store_lock:
        job = _job_store.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        return dict(job)


def _set_job_state(job_id: str, **updates: Any) -> None:
    with _job_store_lock:
        job = _job_store.get(job_id)
        if job is None:
            return
        job.update(updates)


def _create_job(job_type: Literal["workflow", "verification"]) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "job_type": job_type,
        "status": "queued",
        "created_at_epoch": time.time(),
        "started_at_epoch": None,
        "finished_at_epoch": None,
        "result": None,
        "error": None,
    }
    with _job_store_lock:
        _job_store[job_id] = job
    return dict(job)


def _job_response(job: Dict[str, Any]) -> Dict[str, Any]:
    return JobStatusResponse(**job).model_dump()


def _run_job(job_id: str, fn: Any, *args: Any) -> None:
    _set_job_state(job_id, status="running", started_at_epoch=time.time())
    try:
        result = fn(*args)
        _set_job_state(
            job_id,
            status="succeeded",
            result=result,
            finished_at_epoch=time.time(),
        )
    except HTTPException as exc:
        _set_job_state(
            job_id,
            status="failed",
            error={"status_code": exc.status_code, "detail": exc.detail},
            finished_at_epoch=time.time(),
        )
    except Exception as exc:  # pragma: no cover - defensive serialization path
        _set_job_state(
            job_id,
            status="failed",
            error={"status_code": 500, "detail": str(exc)},
            finished_at_epoch=time.time(),
        )


def _run_workflow_execution(req: ExecuteWorkflowRequest) -> Dict[str, Any]:
    vr = validate_workflow_dict(req.workflow)
    if not vr.valid:
        raise HTTPException(
            status_code=400,
            detail={
                "validation": {
                    "valid": vr.valid,
                    "issues": _serialize_validation_issues(vr.issues),
                },
                "execution": None,
            },
        )

    result = run_workflow_from_dict(req.workflow, save_path=req.save_path, verbose=True)
    return {
        "success": result.success,
        "validation": {
            "valid": True,
            "issues": [],
        },
        "execution": {
            "saved_to": result.saved_to,
            "summary": result.summary,
            "error": result.error,
        },
    }


def _resolve_relative_paths_in_case_suite(
    case_suite: Dict[str, Any], case_file_path: str
) -> None:
    """Resolve relative paths in verification cases to be absolute paths.
    
    This function modifies the case_suite in-place, converting relative paths in simulation_IO
    to absolute paths. It tries multiple resolution strategies:
    1. Check if path is already absolute or Windows path
    2. Try resolving relative to /data (for data, schema subdirs)
    3. Try resolving relative to /app (for resources, weather subdirs)
    4. Fall back to resolving relative to case file directory
    
    Args:
        case_suite: Dictionary of verification cases keyed by case ID
        case_file_path: Absolute path to the verification case JSON file
    """
    case_dir = str(Path(case_file_path).parent.resolve())
    
    def resolve_path(path_str: str) -> str:
        """Resolve a single path string to an absolute path."""
        if not path_str:
            return path_str
            
        path_str = path_str.strip()
        
        # Already absolute or Windows path - return as-is
        if path_str.startswith("/") or path_str.startswith("~") or (len(path_str) >= 2 and path_str[1] == ":"):
            return str(Path(path_str).expanduser().resolve())
        
        # Try relative to /data first (for ./data/... paths)
        if path_str.startswith("./data/") or path_str.startswith("./schema/"):
            candidate = Path("/data") / path_str.lstrip("./")
            if candidate.exists():
                return str(candidate.resolve())
        
        # Try relative to /app (for ./resources/... and ./weather/... paths)
        if path_str.startswith("./resources/") or path_str.startswith("./weather/"):
            candidate = Path("/app") / path_str.lstrip("./")
            if candidate.exists():
                return str(candidate.resolve())
        
        # Fall back to resolving relative to case directory
        candidate = Path(case_dir) / path_str
        if candidate.exists():
            return str(candidate.resolve())
        
        # If nothing exists, return the /data or /app based guess anyway (for better error messages)
        if path_str.startswith("./data/") or path_str.startswith("./schema/"):
            return str((Path("/data") / path_str.lstrip("./")).resolve())
        elif path_str.startswith("./resources/") or path_str.startswith("./weather/"):
            return str((Path("/app") / path_str.lstrip("./")).resolve())
        else:
            return str((Path(case_dir) / path_str).resolve())
    
    for case_id, case in case_suite.items():
        if "simulation_IO" in case:
            sim_io = case["simulation_IO"]
            # List of path fields that might be relative
            path_fields = ["idf", "idd", "weather", "output", "ep_path"]
            
            for field in path_fields:
                if field in sim_io and isinstance(sim_io[field], str):
                    sim_io[field] = resolve_path(sim_io[field])


def _run_verification_execution(req: ExecuteVerificationRequest) -> Dict[str, Any]:
    if not os.path.isfile(req.case_file_path):
        raise HTTPException(
            status_code=400,
            detail=f"Verification case file not found: {req.case_file_path}",
        )

    os.makedirs(req.output_dir, exist_ok=True)

    if req.library_json_path:
        library_json_path = req.library_json_path
    else:
        library_json_path = str(
            Path(__file__).resolve().parents[1] / "schema/library.json"
        )

    if not os.path.isfile(library_json_path):
        raise HTTPException(
            status_code=400,
            detail=f"Library JSON file not found: {library_json_path}",
        )

    if len(req.fig_size) != 2:
        raise HTTPException(
            status_code=400,
            detail="fig_size must contain exactly two numbers: [width, height].",
        )

    if req.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise HTTPException(
            status_code=400,
            detail="log_level must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.",
        )

    logging.getLogger().setLevel(getattr(logging, req.log_level.upper()))

    try:
        verification_case = VerificationCase(json_case_path=req.case_file_path)
        if len(verification_case.case_suite) == 0:
            raise HTTPException(
                status_code=400,
                detail="No verification cases were loaded from the provided JSON file.",
            )
        
        # Resolve relative paths in the verification case relative to the case file directory
        _resolve_relative_paths_in_case_suite(
            verification_case.case_suite, req.case_file_path
        )

        preprocessed_data = None
        if req.data_file_path:
            if not os.path.isfile(req.data_file_path):
                raise HTTPException(
                    status_code=400,
                    detail=f"Data file not found: {req.data_file_path}",
                )
            data_processing = DataProcessing(
                data_path=req.data_file_path,
                data_source=req.data_source,
            )
            preprocessed_data = data_processing.data
            if preprocessed_data is None:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to load preprocessed data from the provided data file.",
                )

        verification = Verification(verifications=verification_case)

        tolerances_file_path = req.tolerances_file_path
        if tolerances_file_path is None:
            tolerances_file_path = str(
                Path(__file__).resolve().parents[1] / "tolerances.json"
            )

        verification.configure(
            output_path=req.output_dir,
            lib_items_path=library_json_path,
            plot_option=req.plot_option,
            fig_size=(req.fig_size[0], req.fig_size[1]),
            num_threads=1,
            preprocessed_data=preprocessed_data,
            path_to_custom_tolerance_file=tolerances_file_path,
        )
        verification.run()

        md_json_files = sorted(glob.glob(os.path.join(req.output_dir, "*_md.json")))
        summary_path = None

        if req.generate_summary and md_json_files:
            reporting = Reporting(
                verification_json=os.path.join(req.output_dir, "*_md.json"),
                result_md_name=req.summary_file_name,
                report_format="markdown",
            )
            reporting.report_multiple_cases(item_names=req.report_item_names or [])
            summary_path = reporting.result_md_path

        return {
            "success": True,
            "verification": {
                "case_file_path": req.case_file_path,
                "output_dir": req.output_dir,
                "md_json_files": md_json_files,
            },
            "reporting": {
                "generated": bool(summary_path),
                "summary_path": summary_path,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Verification execution failed: {exc}",
        ) from exc


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "constrain-api-server"}


@app.post("/ai/workflow/suggest")
def api_suggest_workflow(req: WorkflowSuggestRequest) -> Dict[str, Any]:
    _ensure_llm_available()
    result: ComposerResult = suggest_workflow(
        goal_description=req.goal_description,
        data_context=req.data_context,
        existing_workflow=req.existing_workflow,
        cases_context=req.cases_context,
    )
    return {
        "ok": result.ok,
        "workflow": result.data,
        "validation": {
            "valid": result.validation.valid,
            "issues": _serialize_validation_issues(result.validation.issues),
        },
        "raw_text": result.raw_text,
    }


@app.post("/ai/cases/suggest")
def api_suggest_cases(req: CasesSuggestRequest) -> Dict[str, Any]:
    _ensure_llm_available()
    result: ComposerResult = suggest_verification_cases(
        goal_description=req.goal_description,
        signals_available=req.signals_available,
        existing_cases=req.existing_cases,
    )
    return {
        "ok": result.ok,
        "cases": result.data,
        "validation": {
            "valid": result.validation.valid,
            "issues": _serialize_validation_issues(result.validation.issues),
        },
        "raw_text": result.raw_text,
    }


@app.post("/ai/workflow/validate")
def api_validate_workflow(req: ValidateWorkflowRequest) -> Dict[str, Any]:
    vr = validate_workflow_dict(req.workflow)
    return {
        "valid": vr.valid,
        "issues": _serialize_validation_issues(vr.issues),
    }


@app.post("/ai/cases/validate")
def api_validate_cases(req: ValidateCasesRequest) -> Dict[str, Any]:
    vr = validate_case_suite_dict(req.cases)
    return {
        "valid": vr.valid,
        "issues": _serialize_validation_issues(vr.issues),
    }


@app.get("/ai/catalog")
def api_catalog() -> Dict[str, Any]:
    """Return catalogs of callables and verification classes."""
    return {
        "callables": as_serializable(list_workflow_callables()),
        "verification_classes": as_serializable(list_verification_classes()),
    }


@app.post("/ai/workflow/execute")
def api_execute_workflow(req: ExecuteWorkflowRequest) -> Dict[str, Any]:
    """Validate and execute a workflow definition."""
    return _run_workflow_execution(req)


@app.post("/ai/workflow/jobs")
def api_submit_workflow_job(req: ExecuteWorkflowRequest) -> Dict[str, Any]:
    """Submit a workflow job and return a polling handle."""
    job = _create_job("workflow")
    _job_executor.submit(_run_job, job["job_id"], _run_workflow_execution, req)
    return _job_response(job)


@app.post("/ai/verification/execute")
def api_execute_verification(req: ExecuteVerificationRequest) -> Dict[str, Any]:
    """Execute verification cases from JSON, and optionally generate a summary report."""
    return _run_verification_execution(req)


@app.post("/ai/verification/jobs")
def api_submit_verification_job(req: ExecuteVerificationRequest) -> Dict[str, Any]:
    """Submit a verification job and return a polling handle."""
    job = _create_job("verification")
    _job_executor.submit(_run_job, job["job_id"], _run_verification_execution, req)
    return _job_response(job)


@app.get("/ai/jobs/{job_id}")
def api_get_job(job_id: str) -> Dict[str, Any]:
    """Return status and result metadata for an asynchronous job."""
    return _job_response(_get_job(job_id))


@app.get("/ai/artifacts/list")
def api_list_artifacts(
    output_dir: str = Query(
        ..., description="Directory containing generated artifacts."
    ),
    recursive: bool = Query(True, description="List files recursively."),
) -> Dict[str, Any]:
    output_dir_path = _resolve_output_dir(output_dir)

    file_paths = output_dir_path.rglob("*") if recursive else output_dir_path.glob("*")
    artifacts = []
    for file_path in sorted(path for path in file_paths if path.is_file()):
        stat = file_path.stat()
        artifacts.append(
            {
                "relative_path": str(file_path.relative_to(output_dir_path)),
                "size_bytes": stat.st_size,
                "modified_epoch": int(stat.st_mtime),
            }
        )

    return {
        "output_dir": str(output_dir_path),
        "count": len(artifacts),
        "artifacts": artifacts,
    }


@app.get("/ai/artifacts/download")
def api_download_artifact(
    output_dir: str = Query(
        ..., description="Directory containing generated artifacts."
    ),
    relative_path: str = Query(
        ..., description="Relative path of artifact to download."
    ),
) -> FileResponse:
    output_dir_path = _resolve_output_dir(output_dir)
    artifact_path = _resolve_artifact_path(output_dir_path, relative_path)
    return FileResponse(
        path=str(artifact_path),
        filename=artifact_path.name,
        media_type="application/octet-stream",
    )


@app.get("/ai/artifacts/download-zip")
def api_download_artifacts_zip(
    output_dir: str = Query(
        ..., description="Directory containing generated artifacts."
    ),
) -> StreamingResponse:
    output_dir_path = _resolve_output_dir(output_dir)
    files = sorted(path for path in output_dir_path.rglob("*") if path.is_file())
    if not files:
        raise HTTPException(status_code=404, detail="No artifacts found to zip.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            zf.write(file_path, arcname=str(file_path.relative_to(output_dir_path)))
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="verification_results.zip"'
        },
    )


__all__ = ["app"]
