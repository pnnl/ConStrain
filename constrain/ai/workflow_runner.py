"""
Helpers to execute ConStrain workflows from JSON definitions.

These utilities are intended to be used by the AI workflow composer server
and UI to run AI-generated workflows after they have been validated.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from constrain.api.workflow import Workflow


@dataclass
class WorkflowExecutionResult:
    """Summary of a workflow execution."""

    success: bool
    saved_to: Optional[str]
    summary: Optional[Dict[str, Any]]
    error: Optional[str] = None


def _ensure_parent_dir(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def run_workflow_from_files(workflow_path: str, verbose: bool = True) -> WorkflowExecutionResult:
    """Run a workflow from a JSON file path."""
    wf = Workflow(workflow=workflow_path)
    try:
        wf.run_workflow(verbose=verbose)
        summary = None
        try:
            summary = wf.workflow_engine.summarize_workflow_run()
        except Exception:
            summary = None
        return WorkflowExecutionResult(
            success=True,
            saved_to=workflow_path,
            summary=summary,
        )
    except Exception as exc:
        return WorkflowExecutionResult(
            success=False,
            saved_to=workflow_path,
            summary=None,
            error=str(exc),
        )


def run_workflow_from_dict(
    workflow_dict: Dict[str, Any],
    save_path: Optional[str] = None,
    verbose: bool = True,
) -> WorkflowExecutionResult:
    """Run a workflow from an in-memory dict, optionally saving it first."""
    saved_to: Optional[str] = None

    if save_path is not None:
        path = Path(save_path)
        _ensure_parent_dir(path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(workflow_dict, f, indent=2)
        saved_to = str(path)
        workflow_input: Any = saved_to
    else:
        workflow_input = workflow_dict

    wf = Workflow(workflow=workflow_input)
    try:
        wf.run_workflow(verbose=verbose)
        summary = None
        try:
            summary = wf.workflow_engine.summarize_workflow_run()
        except Exception:
            summary = None
        return WorkflowExecutionResult(
            success=True,
            saved_to=saved_to,
            summary=summary,
        )
    except Exception as exc:
        return WorkflowExecutionResult(
            success=False,
            saved_to=saved_to,
            summary=None,
            error=str(exc),
        )


__all__ = ["WorkflowExecutionResult", "run_workflow_from_files", "run_workflow_from_dict"]

