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

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
            "issues": [
                {
                    "loc": issue.loc,
                    "message": issue.message,
                    "validator": issue.validator,
                }
                for issue in result.validation.issues
            ],
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
            "issues": [
                {
                    "loc": issue.loc,
                    "message": issue.message,
                    "validator": issue.validator,
                }
                for issue in result.validation.issues
            ],
        },
        "raw_text": result.raw_text,
    }


@app.post("/ai/workflow/validate")
def api_validate_workflow(req: ValidateWorkflowRequest) -> Dict[str, Any]:
    vr = validate_workflow_dict(req.workflow)
    return {
        "valid": vr.valid,
        "issues": [
            {"loc": issue.loc, "message": issue.message, "validator": issue.validator}
            for issue in vr.issues
        ],
    }


@app.post("/ai/cases/validate")
def api_validate_cases(req: ValidateCasesRequest) -> Dict[str, Any]:
    vr = validate_case_suite_dict(req.cases)
    return {
        "valid": vr.valid,
        "issues": [
            {"loc": issue.loc, "message": issue.message, "validator": issue.validator}
            for issue in vr.issues
        ],
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
    vr = validate_workflow_dict(req.workflow)
    if not vr.valid:
        return {
            "success": False,
            "validation": {
                "valid": vr.valid,
                "issues": [
                    {
                        "loc": issue.loc,
                        "message": issue.message,
                        "validator": issue.validator,
                    }
                    for issue in vr.issues
                ],
            },
            "execution": None,
        }

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


__all__ = ["app"]

