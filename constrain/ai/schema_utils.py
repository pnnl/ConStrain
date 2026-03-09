"""
Schema-backed validation helpers for workflows and verification cases.

These utilities wrap the existing ConStrain validation logic in a
machine-friendly contract that AI-assisted tools and web APIs can use.

Key responsibilities:
- Load and cache the workflow JSON Schema (`schema/workflow.schema.json`).
- Provide helpers to validate a workflow dict with both the JSON Schema
  and the `Workflow` API's own structural checks.
- Provide helpers to validate verification-case JSON suites using
  `VerificationCase.validate_verification_case_structure`.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from importlib import resources
from typing import Any, Dict, List, Optional, Tuple, Union

from jsonschema import Draft202012Validator, ValidationError

from constrain.api.workflow import Workflow
from constrain.api.verification_case import VerificationCase


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    loc: List[Union[str, int]]
    message: str
    validator: Optional[str] = None


@dataclass
class ValidationResult:
    """Aggregated validation result."""

    valid: bool
    issues: List[ValidationIssue]


_WORKFLOW_SCHEMA_CACHE: Optional[Dict[str, Any]] = None
_WORKFLOW_VALIDATOR_CACHE: Optional[Draft202012Validator] = None


def _load_workflow_schema() -> Dict[str, Any]:
    """Load the workflow JSON Schema from `constrain/schema/workflow.schema.json`."""
    global _WORKFLOW_SCHEMA_CACHE
    if _WORKFLOW_SCHEMA_CACHE is not None:
        return _WORKFLOW_SCHEMA_CACHE

    # Use importlib.resources so this works both in a source checkout and an installed package.
    with resources.files("constrain.schema").joinpath("workflow.schema.json").open(
        "r", encoding="utf-8"
    ) as f:
        _WORKFLOW_SCHEMA_CACHE = json.load(f)
    return _WORKFLOW_SCHEMA_CACHE


def _get_workflow_validator() -> Draft202012Validator:
    """Return a cached `jsonschema` validator for workflow definitions."""
    global _WORKFLOW_VALIDATOR_CACHE
    if _WORKFLOW_VALIDATOR_CACHE is not None:
        return _WORKFLOW_VALIDATOR_CACHE

    schema = _load_workflow_schema()
    _WORKFLOW_VALIDATOR_CACHE = Draft202012Validator(schema)
    return _WORKFLOW_VALIDATOR_CACHE


def validate_workflow_dict(workflow: Dict[str, Any]) -> ValidationResult:
    """Validate a workflow dict using both JSON Schema and `Workflow.validate`.

    This function does **not** consider whether referenced functions exist
    or are importable; it only checks the structural aspects of the workflow
    JSON itself.
    """
    issues: List[ValidationIssue] = []

    # 1) JSON Schema validation
    validator = _get_workflow_validator()
    for error in validator.iter_errors(workflow):
        issues.append(
            ValidationIssue(
                loc=list(error.path),
                message=error.message,
                validator=error.validator,
            )
        )

    # 2) Python-side validation via Workflow API (high-level schema)
    try:
        # `Workflow.validate_workflow_definition` returns a bool in current implementation.
        wf_ok = Workflow.validate_workflow_definition(workflow, verbose=False)
        if not wf_ok:
            issues.append(
                ValidationIssue(
                    loc=[],
                    message="WorkflowEngine.validate reported the workflow as invalid.",
                    validator="WorkflowEngine.validate",
                )
            )
    except Exception as exc:  # pragma: no cover - defensive
        logging.exception("Error during Workflow.validate_workflow_definition: %s", exc)
        issues.append(
            ValidationIssue(
                loc=[],
                message=f"Exception during Workflow validation: {exc}",
                validator="WorkflowEngine.validate",
            )
        )

    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_workflow_json_str(workflow_json: str) -> Tuple[Optional[Dict[str, Any]], ValidationResult]:
    """Parse and validate a workflow definition from a JSON string."""
    try:
        workflow_dict = json.loads(workflow_json)
    except json.JSONDecodeError as e:
        vr = ValidationResult(
            valid=False,
            issues=[
                ValidationIssue(
                    loc=[],
                    message=f"Invalid JSON: {e}",
                    validator="json",
                )
            ],
        )
        return None, vr

    return workflow_dict, validate_workflow_dict(workflow_dict)


def validate_case_suite_dict(case_suite: Dict[str, Any]) -> ValidationResult:
    """Validate a verification-case suite dict of the form:

        {
          "cases": [ { ...case1... }, { ...case2... }, ... ]
        }

    using `VerificationCase.validate_verification_case_structure` on each case.
    """
    issues: List[ValidationIssue] = []

    cases = case_suite.get("cases")
    if not isinstance(cases, list):
        return ValidationResult(
            valid=False,
            issues=[
                ValidationIssue(
                    loc=["cases"],
                    message="Top-level key 'cases' must be a list.",
                    validator="structure",
                )
            ],
        )

    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(
                ValidationIssue(
                    loc=["cases", idx],
                    message="Each case must be an object.",
                    validator="type",
                )
            )
            continue

        ok = VerificationCase.validate_verification_case_structure(case, verbose=False)
        if not ok:
            issues.append(
                ValidationIssue(
                    loc=["cases", idx],
                    message="Case failed VerificationCase.validate_verification_case_structure.",
                    validator="VerificationCase.validate_verification_case_structure",
                )
            )

    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_case_suite_json_str(
    case_suite_json: str,
) -> Tuple[Optional[Dict[str, Any]], ValidationResult]:
    """Parse and validate a verification-case suite from a JSON string."""
    try:
        case_suite_dict = json.loads(case_suite_json)
    except json.JSONDecodeError as e:
        vr = ValidationResult(
            valid=False,
            issues=[
                ValidationIssue(
                    loc=[],
                    message=f"Invalid JSON: {e}",
                    validator="json",
                )
            ],
        )
        return None, vr

    return case_suite_dict, validate_case_suite_dict(case_suite_dict)


__all__ = [
    "ValidationIssue",
    "ValidationResult",
    "validate_workflow_dict",
    "validate_workflow_json_str",
    "validate_case_suite_dict",
    "validate_case_suite_json_str",
]

