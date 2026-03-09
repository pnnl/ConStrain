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
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from constrain.ai.schema_utils import (
    validate_case_suite_json_str,
    validate_workflow_json_str,
)
from constrain.ai.workflow_composer import (
    suggest_verification_cases,
    suggest_workflow,
)


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
        },
    )


__all__ = ["app"]

