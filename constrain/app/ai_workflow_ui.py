"""
Simple web UI for the AI workflow composer.

This module provides a minimal FastAPI application with Jinja2 templates to
interact with the AI endpoints defined in `ai_workflow_server.py`. It is
intended as a lightweight starting point rather than a full-featured GUI.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen
from typing import Any, Dict, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from constrain.ai.schema_utils import (
    validate_workflow_json_str,
)
from constrain.ai.llm_client import HTTPJSONLLMClient, LLMConfig
from constrain.ai.workflow_composer import (
    _build_cases_system_prompt,
    _build_workflow_system_prompt,
    suggest_verification_cases,
    suggest_workflow,
)


app = FastAPI(title="ConStrain AI Workflow Composer UI")
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent / "templates")
)
_COMPOSE_DEBUG_REPORTS: Dict[str, Dict[str, Any]] = {}


def _build_workflow_user_prompt(
    goal_description: str,
    data_context: Optional[Dict[str, Any]],
    existing_workflow: Optional[Dict[str, Any]],
    cases_context: Optional[Dict[str, Any]],
) -> str:
    user_parts = ["User goal:\n", goal_description]
    if data_context:
        user_parts.append("\nData context (paths, formats, notes):\n")
        user_parts.append(json.dumps(data_context, indent=2, default=str))
    if existing_workflow:
        user_parts.append("\nExisting workflow to refine (JSON):\n")
        user_parts.append(json.dumps(existing_workflow, indent=2, default=str))
    if cases_context:
        user_parts.append("\nVerification-case context (JSON):\n")
        user_parts.append(json.dumps(cases_context, indent=2, default=str))
    return "\n".join(user_parts)


def _build_cases_user_prompt(
    goal_description: str,
    signals_available: Optional[Dict[str, Any]],
    existing_cases: Optional[Dict[str, Any]],
) -> str:
    user_parts = ["User goal for verification cases:\n", goal_description]
    if signals_available:
        user_parts.append("\nSignals / datapoints available:\n")
        user_parts.append(json.dumps(signals_available, indent=2, default=str))
    if existing_cases:
        user_parts.append("\nExisting verification-case suite to refine (JSON):\n")
        user_parts.append(json.dumps(existing_cases, indent=2, default=str))
    return "\n".join(user_parts)


def _build_compose_debug_markdown(
    goal: str,
    wf_system_prompt: str,
    wf_user_prompt: str,
    wf_raw_response: str,
    cases_system_prompt: str,
    cases_user_prompt: str,
    cases_raw_response: str,
) -> str:
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    return "\n".join(
        [
            "# Workflow Composer Debug Report",
            "",
            f"Generated at: {now}",
            "",
            "## Goal",
            "",
            goal,
            "",
            "## Workflow Suggestion Prompt",
            "",
            "### System Prompt",
            "",
            "```text",
            wf_system_prompt,
            "```",
            "",
            "### User Prompt",
            "",
            "```text",
            wf_user_prompt,
            "```",
            "",
            "### Raw LLM Response",
            "",
            "```text",
            wf_raw_response,
            "```",
            "",
            "## Verification Cases Suggestion Prompt",
            "",
            "### System Prompt",
            "",
            "```text",
            cases_system_prompt,
            "```",
            "",
            "### User Prompt",
            "",
            "```text",
            cases_user_prompt,
            "```",
            "",
            "### Raw LLM Response",
            "",
            "```text",
            cases_raw_response,
            "```",
            "",
        ]
    )


def _store_compose_debug_markdown(content: str) -> str:
    debug_id = str(uuid.uuid4())
    _COMPOSE_DEBUG_REPORTS[debug_id] = {
        "created_at_epoch": time.time(),
        "content": content,
    }
    return debug_id


def _render_page(
    request: Request,
    context: Dict[str, Any],
    template_name: str = "ai_workflow_index.html",
) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=context,
        )
    except Exception as exc:
        verification_result = context.get("verification_result")
        execution_summary = context.get("execution_summary")
        artifacts = context.get("artifacts") or []
        artifact_items = "".join(
            (
                '<li><a href="/artifact/download?output_dir={output_dir}&relative_path={relative_path}">{name}</a></li>'
            ).format(
                output_dir=escape(
                    str(context.get("artifacts_output_dir", "")), quote=True
                ),
                relative_path=escape(str(item.get("relative_path", "")), quote=True),
                name=escape(str(item.get("relative_path", "artifact"))),
            )
            for item in artifacts
        )
        fallback_sections = []
        if verification_result is not None:
            fallback_sections.append(
                "<h2>Verification Result</h2><pre>{}</pre>".format(
                    escape(json.dumps(verification_result, indent=2, default=str))
                )
            )
        if context.get("verification_error"):
            fallback_sections.append(
                "<h2>Verification Error</h2><pre>{}</pre>".format(
                    escape(str(context["verification_error"]))
                )
            )
        if execution_summary is not None:
            fallback_sections.append(
                "<h2>Execution Summary</h2><pre>{}</pre>".format(
                    escape(json.dumps(execution_summary, indent=2, default=str))
                )
            )
        if context.get("execution_error"):
            fallback_sections.append(
                "<h2>Execution Error</h2><pre>{}</pre>".format(
                    escape(str(context["execution_error"]))
                )
            )
        if artifacts:
            fallback_sections.append(
                "<h2>Artifacts</h2><ul>{}</ul>".format(artifact_items)
            )

        html = "".join(
            [
                '<!doctype html><html><head><meta charset="utf-8"><title>ConStrain AI Workflow Composer</title></head><body>',
                "<h1>ConStrain AI Workflow Composer</h1>",
                "<p>Template rendering fallback was used.</p>",
                '<p><a href="/">Home</a> | <a href="/workflow">Workflow Composer</a> | <a href="/verification">Verification Execution</a></p>',
                "<p><strong>Template error:</strong> {}</p>".format(escape(str(exc))),
                *fallback_sections,
                "</body></html>",
            ]
        )
        return HTMLResponse(content=html, status_code=200)


def _render_landing_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="ai_workflow_landing.html",
        context={"request": request},
    )


def _render_workflow_page(request: Request, context: Dict[str, Any]) -> HTMLResponse:
    return _render_page(request, context, template_name="ai_workflow_index.html")


def _render_verification_page(
    request: Request, context: Dict[str, Any]
) -> HTMLResponse:
    return _render_page(
        request,
        context,
        template_name="ai_workflow_verification.html",
    )


def _api_base_url() -> str:
    return os.getenv("CONSTRAIN_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _public_api_base_url() -> str:
    return os.getenv("CONSTRAIN_PUBLIC_API_BASE_URL", "http://127.0.0.1:8000").rstrip(
        "/"
    )


def _api_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    request = UrlRequest(
        f"{_api_base_url()}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = None
        try:
            raw_body = exc.read().decode("utf-8")
            payload = json.loads(raw_body)
            detail = payload.get("detail")
        except Exception:
            detail = None

        if detail is not None:
            raise RuntimeError(f"API error {exc.code}: {detail}") from exc
        raise RuntimeError(f"API error {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Unable to reach API server: {exc.reason}") from exc


def _api_get(path: str, query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    query_str = f"?{urlencode(query or {}, doseq=True)}" if query else ""
    try:
        with urlopen(f"{_api_base_url()}{path}{query_str}", timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"API error {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Unable to reach API server: {exc.reason}") from exc


def _wait_for_job(job_id: str, timeout_seconds: float = 120.0) -> Dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_payload: Optional[Dict[str, Any]] = None

    while time.time() < deadline:
        last_payload = _api_get(f"/ai/jobs/{job_id}")
        status = last_payload.get("status")
        if status == "succeeded":
            return last_payload.get("result") or {}
        if status == "failed":
            error = last_payload.get("error") or {}
            detail = error.get("detail", "Job execution failed.")
            raise RuntimeError(str(detail))
        time.sleep(0.25)

    raise TimeoutError(
        f"Job {job_id} did not complete within {timeout_seconds:.0f} seconds. Last status: "
        f"{(last_payload or {}).get('status', 'unknown')}"
    )


def _base_context(request: Request) -> Dict[str, Any]:
    return {
        "request": request,
        "workflow_json": "",
        "cases_json": "",
        "workflow_issues": [],
        "cases_issues": [],
        "goal": "",
        "compose_error": None,
        "compose_debug_download_path": "",
        "execution_summary": None,
        "execution_error": None,
        "verification_result": None,
        "verification_error": None,
        "artifacts": [],
        "artifacts_output_dir": "",
        "api_base_url": _public_api_base_url(),
        "llm_settings": {
            "api_base": os.getenv("CONSTRAIN_LLM_API_BASE", ""),
            "model": os.getenv("CONSTRAIN_LLM_MODEL", ""),
            "api_key": "",
            "timeout": os.getenv("CONSTRAIN_LLM_TIMEOUT", ""),
        },
        "verification_inputs": {
            "case_file_path": "",
            "output_dir": "",
            "data_file_path": "",
            "library_json_path": "",
            "plot_option": "all-compact",
            "fig_width": "6.4",
            "fig_height": "4.8",
            "tolerances_file_path": "",
            "log_level": "INFO",
            "summary_file_name": "verification_summary.md",
            "report_item_names": "",
            "generate_summary": True,
        },
    }


def _normalize_llm_settings(raw_settings: Dict[str, str]) -> Dict[str, str]:
    return {
        "api_base": (raw_settings.get("api_base") or "").strip(),
        "model": (raw_settings.get("model") or "").strip(),
        "api_key": (raw_settings.get("api_key") or "").strip(),
        "timeout": (raw_settings.get("timeout") or "").strip(),
    }


def _build_llm_client_from_form(
    settings: Dict[str, str]
) -> Optional[HTTPJSONLLMClient]:
    normalized = _normalize_llm_settings(settings)
    has_any_value = any(normalized.values())
    if not has_any_value:
        return None

    api_base = normalized["api_base"]
    model = normalized["model"]
    if not api_base or not model:
        raise RuntimeError(
            "When setting LLM options in the page, both API base URL and model are required."
        )

    timeout = 30.0
    if normalized["timeout"]:
        try:
            timeout = float(normalized["timeout"])
        except ValueError as exc:
            raise RuntimeError("LLM timeout must be a valid number.") from exc
        if timeout <= 0:
            raise RuntimeError("LLM timeout must be greater than zero.")

    config = LLMConfig(
        api_base=api_base,
        api_key=normalized["api_key"],
        model=model,
        timeout=timeout,
    )
    return HTTPJSONLLMClient(config)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "constrain-api-ui"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return _render_landing_page(request)


@app.get("/workflow", response_class=HTMLResponse)
def workflow_page(request: Request) -> HTMLResponse:
    return _render_workflow_page(request, _base_context(request))


@app.get("/verification", response_class=HTMLResponse)
def verification_page(request: Request) -> HTMLResponse:
    return _render_verification_page(request, _base_context(request))


@app.post("/compose", response_class=HTMLResponse)
def compose(
    request: Request,
    goal: str = Form(...),
    data_source_annotation: str = Form(""),
    existing_workflow: str = Form(""),
    existing_cases: str = Form(""),
    llm_api_base: str = Form(""),
    llm_model: str = Form(""),
    llm_api_key: str = Form(""),
    llm_timeout: str = Form(""),
) -> HTMLResponse:
    context = _base_context(request)
    context["goal"] = goal
    context["llm_settings"] = _normalize_llm_settings(
        {
            "api_base": llm_api_base,
            "model": llm_model,
            "api_key": llm_api_key,
            "timeout": llm_timeout,
        }
    )

    # Parse optional JSON: shared context for workflow + verification-case LLM prompts.
    annotation_ctx: Optional[Dict[str, Any]] = None
    if data_source_annotation.strip():
        try:
            annotation_ctx = json.loads(data_source_annotation)
        except json.JSONDecodeError:
            annotation_ctx = None

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

    try:
        llm_client = _build_llm_client_from_form(context["llm_settings"])

        wf_system_prompt = _build_workflow_system_prompt()
        wf_user_prompt = _build_workflow_user_prompt(
            goal_description=goal,
            data_context=annotation_ctx,
            existing_workflow=existing_wf_dict,
            cases_context=existing_cases_dict,
        )
        cases_system_prompt = _build_cases_system_prompt()
        cases_user_prompt = _build_cases_user_prompt(
            goal_description=goal,
            signals_available=annotation_ctx,
            existing_cases=existing_cases_dict,
        )

        wf_result = suggest_workflow(
            goal_description=goal,
            data_context=annotation_ctx,
            existing_workflow=existing_wf_dict,
            cases_context=existing_cases_dict,
            llm_client=llm_client,
        )
        cases_result = suggest_verification_cases(
            goal_description=goal,
            signals_available=annotation_ctx,
            existing_cases=existing_cases_dict,
            llm_client=llm_client,
        )

        workflow_json = json.dumps(wf_result.data or {}, indent=2)
        cases_json = json.dumps(cases_result.data or {}, indent=2)

        context.update(
            {
                "workflow_json": workflow_json,
                "cases_json": cases_json,
                "workflow_issues": wf_result.validation.issues,
                "cases_issues": cases_result.validation.issues,
            }
        )

        debug_markdown = _build_compose_debug_markdown(
            goal=goal,
            wf_system_prompt=wf_system_prompt,
            wf_user_prompt=wf_user_prompt,
            wf_raw_response=wf_result.raw_text,
            cases_system_prompt=cases_system_prompt,
            cases_user_prompt=cases_user_prompt,
            cases_raw_response=cases_result.raw_text,
        )
        debug_id = _store_compose_debug_markdown(debug_markdown)
        context["compose_debug_download_path"] = (
            f"/compose/debug-report/{debug_id}.md"
        )
    except Exception as exc:
        context["compose_error"] = str(exc)

    return _render_workflow_page(request, context)


@app.get("/compose/debug-report/{debug_id}.md")
def download_compose_debug_report(debug_id: str) -> PlainTextResponse:
    report = _COMPOSE_DEBUG_REPORTS.get(debug_id)
    if report is None:
        return PlainTextResponse("Debug report not found.", status_code=404)

    headers = {
        "Content-Disposition": (
            f'attachment; filename="workflow-composer-debug-{debug_id}.md"'
        )
    }
    return PlainTextResponse(
        str(report.get("content", "")),
        media_type="text/markdown; charset=utf-8",
        headers=headers,
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
        try:
            job = _api_post(
                "/ai/workflow/jobs", {"workflow": wf_dict, "save_path": None}
            )
            result = _wait_for_job(job["job_id"])
            if result.get("success"):
                execution_summary = result.get("execution", {}).get("summary")
            else:
                execution_error = result.get("execution", {}).get("error")
        except Exception as exc:
            execution_error = str(exc)
    elif wf_dict is None:
        execution_error = "Invalid workflow JSON: could not be parsed."
    else:
        # Validation failed
        execution_error = "Workflow failed validation; see issues below."

    context = _base_context(request)
    context.update(
        {
            "workflow_json": workflow_json,
            "cases_json": cases_json,
            "workflow_issues": wf_validation.issues if wf_validation else [],
            "goal": goal,
            "execution_summary": execution_summary,
            "execution_error": execution_error,
        }
    )
    return _render_workflow_page(request, context)


@app.post("/verify", response_class=HTMLResponse)
def verify(
    request: Request,
    case_file_path: str = Form(...),
    output_dir: str = Form(...),
    data_file_path: str = Form(""),
    library_json_path: str = Form(""),
    plot_option: str = Form("all-compact"),
    fig_width: str = Form("6.4"),
    fig_height: str = Form("4.8"),
    tolerances_file_path: str = Form(""),
    log_level: str = Form("INFO"),
    summary_file_name: str = Form("verification_summary.md"),
    report_item_names: str = Form(""),
    generate_summary: Optional[str] = Form(None),
) -> HTMLResponse:
    context = _base_context(request)
    verification_inputs = {
        "case_file_path": case_file_path,
        "output_dir": output_dir,
        "data_file_path": data_file_path,
        "library_json_path": library_json_path,
        "plot_option": plot_option,
        "fig_width": fig_width,
        "fig_height": fig_height,
        "tolerances_file_path": tolerances_file_path,
        "log_level": log_level,
        "summary_file_name": summary_file_name,
        "report_item_names": report_item_names,
        "generate_summary": bool(generate_summary),
    }
    context["verification_inputs"] = verification_inputs

    try:
        report_items = [
            item.strip() for item in report_item_names.split(",") if item.strip()
        ]
        payload = {
            "case_file_path": case_file_path,
            "output_dir": output_dir,
            "data_file_path": data_file_path or None,
            "library_json_path": library_json_path or None,
            "plot_option": plot_option,
            "fig_size": [float(fig_width), float(fig_height)],
            "tolerances_file_path": tolerances_file_path or None,
            "log_level": log_level,
            "generate_summary": bool(generate_summary),
            "summary_file_name": summary_file_name,
            "report_item_names": report_items or None,
        }
        verification_result = _api_post("/ai/verification/execute", payload)
        artifacts_payload = _api_get(
            "/ai/artifacts/list",
            {"output_dir": output_dir, "recursive": True},
        )

        context["verification_result"] = verification_result
        context["artifacts"] = artifacts_payload.get("artifacts", [])
        context["artifacts_output_dir"] = artifacts_payload.get(
            "output_dir", output_dir
        )
    except Exception as exc:
        context["verification_error"] = str(exc)
        context["artifacts_output_dir"] = output_dir

    return _render_verification_page(request, context)


@app.get("/artifact/download")
def artifact_download(output_dir: str, relative_path: str) -> RedirectResponse:
    query = urlencode({"output_dir": output_dir, "relative_path": relative_path})
    return RedirectResponse(
        url=f"{_public_api_base_url()}/ai/artifacts/download?{query}"
    )


@app.get("/artifact/download-zip")
def artifact_download_zip(output_dir: str) -> RedirectResponse:
    query = urlencode({"output_dir": output_dir})
    return RedirectResponse(
        url=f"{_public_api_base_url()}/ai/artifacts/download-zip?{query}"
    )


__all__ = ["app"]
