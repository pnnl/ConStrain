"""
Simple web UI for the AI workflow composer.

This module provides a minimal FastAPI application with Jinja2 templates to
interact with the AI endpoints defined in `ai_workflow_server.py`. It is
intended as a lightweight starting point rather than a full-featured GUI.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from constrain.ai.schema_utils import (
    validate_workflow_json_str,
)
from constrain.ai.workflow_composer import (
    suggest_verification_cases,
    suggest_workflow,
)
from constrain.ai.workflow_runner import run_workflow_from_dict


app = FastAPI(title="ConStrain AI Workflow Composer UI")
templates = Jinja2Templates(directory="constrain/app/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "ai_workflow_index.html",
        {
            "request": request,
            "workflow_json": "",
            "cases_json": "",
            "workflow_issues": [],
            "cases_issues": [],
            "goal": "",
            "execution_summary": None,
            "execution_error": None,
        },
    )


@app.post("/compose", response_class=HTMLResponse)
def compose(
    request: Request,
    goal: str = Form(...),
    data_context: str = Form(""),
    signals: str = Form(""),
    existing_workflow: str = Form(""),
    existing_cases: str = Form(""),
) -> HTMLResponse:
    # Parse optional JSON inputs if provided.
    data_ctx: Optional[Dict[str, Any]] = None
    if data_context.strip():
        try:
            data_ctx = json.loads(data_context)
        except json.JSONDecodeError:
            data_ctx = None

    signals_ctx: Optional[Dict[str, Any]] = None
    if signals.strip():
        try:
            signals_ctx = json.loads(signals)
        except json.JSONDecodeError:
            signals_ctx = None

    existing_wf_dict: Optional[Dict[str, Any]] = None
    if existing_workflow.strip():
        try:
            existing_wf_dict = json.loads(existing_workflow)
        except json.JSONDecodeError:
            existing_wf_dict = None

    existing_cases_dict: Optional[Dict[str, Any]] = None
    if existing_cases.strip():
        try:
            existing_cases_dict = json.loads(existing_cases)
        except json.JSONDecodeError:
            existing_cases_dict = None

    wf_result = suggest_workflow(
        goal_description=goal,
        data_context=data_ctx,
        existing_workflow=existing_wf_dict,
        cases_context=existing_cases_dict,
    )
    cases_result = suggest_verification_cases(
        goal_description=goal,
        signals_available=signals_ctx,
        existing_cases=existing_cases_dict,
    )

    workflow_json = json.dumps(wf_result.data or {}, indent=2)
    cases_json = json.dumps(cases_result.data or {}, indent=2)

    return templates.TemplateResponse(
        "ai_workflow_index.html",
        {
            "request": request,
            "workflow_json": workflow_json,
            "cases_json": cases_json,
            "workflow_issues": wf_result.validation.issues,
            "cases_issues": cases_result.validation.issues,
            "goal": goal,
            "execution_summary": None,
            "execution_error": None,
        },
    )


@app.post("/run", response_class=HTMLResponse)
def run(
    request: Request,
    workflow_json: str = Form(...),
    cases_json: str = Form(""),
    goal: str = Form(""),
) -> HTMLResponse:
    """Run the provided workflow JSON using the ConStrain API."""
    wf_dict, wf_validation = validate_workflow_json_str(workflow_json)

    execution_summary = None
    execution_error = None

    if wf_dict is not None and wf_validation.valid:
        result = run_workflow_from_dict(wf_dict, save_path=None, verbose=True)
        if result.success:
            execution_summary = result.summary
        else:
            execution_error = result.error
    elif wf_dict is None:
        execution_error = "Invalid workflow JSON: could not be parsed."
    else:
        # Validation failed
        execution_error = "Workflow failed validation; see issues below."

    return templates.TemplateResponse(
        "ai_workflow_index.html",
        {
            "request": request,
            "workflow_json": workflow_json,
            "cases_json": cases_json,
            "workflow_issues": wf_validation.issues if wf_validation else [],
            "cases_issues": [],
            "goal": goal,
            "execution_summary": execution_summary,
            "execution_error": execution_error,
        },
    )


__all__ = ["app"]

