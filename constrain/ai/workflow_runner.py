"""
Helpers to execute ConStrain workflows from JSON definitions.

These utilities are intended to be used by the AI workflow composer server
and UI to run AI-generated workflows after they have been validated.
"""

from __future__ import annotations

import json
import logging
import os
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Package root (constrain/) so that workflow paths like ./demo/G36_demo/... resolve correctly
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _configure_matplotlib_backend() -> None:
    """Force a non-interactive backend so workflow execution is thread-safe on macOS."""
    # Respect user override if provided, otherwise default to a thread-safe backend.
    os.environ.setdefault("MPLBACKEND", "Agg")
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except Exception:
        # Avoid failing workflow execution if matplotlib isn't imported/available here.
        pass


def _get_workflow_class():
    # Lazy import so backend configuration runs before any plotting modules import pyplot.
    from constrain.api.workflow import Workflow

    return Workflow


@dataclass
class WorkflowExecutionResult:
    """Summary of a workflow execution."""

    success: bool
    saved_to: Optional[str]
    summary: Optional[Dict[str, Any]]
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


def _find_state_line_in_workflow_dict(
    workflow_dict: Dict[str, Any], state_name: Optional[str]
) -> Optional[int]:
    """Return 1-based line number of a state key in pretty-printed workflow JSON."""
    if not state_name:
        return None

    try:
        serialized = json.dumps(workflow_dict, indent=2)
        state_token = f"{json.dumps(state_name)}:"
        for idx, line in enumerate(serialized.splitlines(), start=1):
            if state_token in line:
                return idx
    except Exception:
        return None
    return None


def _ensure_parent_dir(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def run_workflow_from_files(
    workflow_path: str, verbose: bool = True
) -> WorkflowExecutionResult:
    """Run a workflow from a JSON file path."""
    _configure_matplotlib_backend()
    Workflow = _get_workflow_class()
    cwd_before = os.getcwd()
    wf = None
    try:
        os.chdir(_PACKAGE_ROOT)
        wf = Workflow(workflow=workflow_path)
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
        tb = traceback.format_exc()
        failing_state = None
        state_line = None
        if wf is not None and hasattr(wf, "workflow_engine"):
            running_sequence = getattr(wf.workflow_engine, "running_sequence", [])
            if isinstance(running_sequence, list) and running_sequence:
                failing_state = running_sequence[-1]
            workflow_dict = getattr(wf.workflow_engine, "workflow_dict", None)
            if isinstance(workflow_dict, dict):
                state_line = _find_state_line_in_workflow_dict(
                    workflow_dict, failing_state
                )

        logger.exception(
            "Workflow execution failed (run_workflow_from_files): %s",
            exc,
            extra={"workflow_path": workflow_path},
        )
        error_message = str(exc)
        if failing_state:
            error_message = f"State '{failing_state}' failed: {exc}"
        return WorkflowExecutionResult(
            success=False,
            saved_to=workflow_path,
            summary=None,
            error=error_message,
            error_details={
                "failing_state": failing_state,
                "state_line": state_line,
                "traceback": tb,
            },
        )
    finally:
        os.chdir(cwd_before)


def run_workflow_from_dict(
    workflow_dict: Dict[str, Any],
    save_path: Optional[str] = None,
    verbose: bool = True,
) -> WorkflowExecutionResult:
    """Run a workflow from an in-memory dict, optionally saving it first."""
    _configure_matplotlib_backend()
    Workflow = _get_workflow_class()
    saved_to: Optional[str] = None
    wf = None

    if save_path is not None:
        path = Path(save_path)
        _ensure_parent_dir(path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(workflow_dict, f, indent=2)
        saved_to = str(path)
        workflow_input: Any = saved_to
    else:
        workflow_input = workflow_dict

    cwd_before = os.getcwd()
    try:
        os.chdir(_PACKAGE_ROOT)
        wf = Workflow(workflow=workflow_input)
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
        tb = traceback.format_exc()
        failing_state = None
        state_line = None
        if wf is not None and hasattr(wf, "workflow_engine"):
            running_sequence = getattr(wf.workflow_engine, "running_sequence", [])
            if isinstance(running_sequence, list) and running_sequence:
                failing_state = running_sequence[-1]
            workflow_dict_loaded = getattr(wf.workflow_engine, "workflow_dict", None)
            if isinstance(workflow_dict_loaded, dict):
                state_line = _find_state_line_in_workflow_dict(
                    workflow_dict_loaded, failing_state
                )
            else:
                state_line = _find_state_line_in_workflow_dict(
                    workflow_dict, failing_state
                )

        logger.exception(
            "Workflow execution failed (run_workflow_from_dict): %s",
            exc,
            extra={"saved_to": saved_to},
        )
        error_message = str(exc)
        if failing_state:
            error_message = f"State '{failing_state}' failed: {exc}"
        return WorkflowExecutionResult(
            success=False,
            saved_to=saved_to,
            summary=None,
            error=error_message,
            error_details={
                "failing_state": failing_state,
                "state_line": state_line,
                "traceback": tb,
            },
        )
    finally:
        os.chdir(cwd_before)


__all__ = [
    "WorkflowExecutionResult",
    "run_workflow_from_files",
    "run_workflow_from_dict",
]
