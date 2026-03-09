"""
High-level AI-assisted composer for workflows and verification cases.

This module ties together:
- The LLM client abstraction (`constrain.ai.llm_client`),
- Schema-backed validation helpers (`constrain.ai.schema_utils`),
- Introspection catalog (`constrain.ai.introspection`),
to provide convenient functions that:

- Propose new workflow JSON definitions from natural-language goals.
- Propose new verification-case suites from natural-language descriptions.
- Optionally refine existing JSON definitions based on edit requests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple

from constrain.ai.introspection import (
    as_serializable,
    list_verification_classes,
    list_workflow_callables,
)
from constrain.ai.llm_client import LLMClient, get_default_llm_client
from constrain.ai.schema_utils import (
    ValidationResult,
    validate_case_suite_dict,
    validate_workflow_dict,
)


@dataclass
class ComposerResult:
    ok: bool
    data: Optional[Dict[str, Any]]
    validation: ValidationResult
    raw_text: str


def _ensure_client(llm_client: Optional[LLMClient]) -> LLMClient:
    client = llm_client or get_default_llm_client()
    if client is None:
        raise RuntimeError(
            "No LLM client configured. Set CONSTRAIN_LLM_API_BASE and "
            "CONSTRAIN_LLM_MODEL (and optionally CONSTRAIN_LLM_API_KEY) "
            "or provide an LLMClient explicitly."
        )
    return client


def _build_workflow_system_prompt() -> str:
    callables = list_workflow_callables()
    verif_classes = list_verification_classes()

    callables_summary = json.dumps(
        as_serializable(callables), indent=2, default=str
    )
    verif_summary = json.dumps(
        as_serializable(verif_classes), indent=2, default=str
    )

    return dedent(
        f"""
        You are an assistant that generates ConStrain workflow JSON definitions.

        A workflow JSON has this high-level structure (see docs and schema for details):
        - workflow_name: string
        - meta: {{ author, date (MM/DD/YYYY), version, description }}
        - imports: array of python import strings
        - states: object mapping state names to state definitions

        Each state is either:
        - Type: "MethodCall"
          - MethodCall: a python expression that resolves to a callable
          - Parameters: object (keyword args) or array (positional args)
          - Payloads: optional object describing how to store results in Payloads
          - Next: optional string name of next state
          - Start / End: optional flags ("True"/"False")
        or
        - Type: "Choice"
          - Choices: array of {{ Value, Equals, Next }} or logical expressions
          - Default: name of next state if no Choice matches

        The following callables are available for MethodCall states:
        {callables_summary}

        The following verification classes are available in the verification library:
        {verif_summary}

        Your job:
        - Propose a COMPLETE workflow JSON as a single JSON object.
        - Use only the provided callables and verification classes.
        - Ensure the result is structurally valid and consistent.
        - Do NOT include comments or extra keys; return pure JSON.
        """
    ).strip()


def _build_cases_system_prompt() -> str:
    verif_classes = list_verification_classes()
    verif_summary = json.dumps(
        as_serializable(verif_classes), indent=2, default=str
    )

    return dedent(
        f"""
        You are an assistant that generates verification-case JSON for ConStrain.

        A verification-case suite JSON has the form:
        {{
          "cases": [
            {{
              "no": <int>,
              "run_simulation": <bool>,
              "simulation_IO": {{
                "output": "<path string>",
                "...": "other optional keys (idf, idd, weather, ep_path)"
              }},
              "expected_result": "<string>",
              "datapoints_source": {{
                "dev_settings": {{ ... arbitrary key->signal-name ... }},
                "parameters": {{ <string>: <float>, ... }}
              }},
              "verification_class": "<string>"
            }},
            ...
          ]
        }}

        The verification_class must correspond to one of the known verification classes below,
        and datapoints/parameters should be consistent with its description:
        {verif_summary}

        Your job:
        - Propose a COMPLETE verification-case suite JSON as a single JSON object.
        - Use only the provided verification classes.
        - Ensure each case is structurally valid.
        - Do NOT include comments or extra keys; return pure JSON.
        """
    ).strip()


def _parse_llm_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract a JSON object from the LLM response.

    The LLM is instructed to return pure JSON, but we still defensively
    handle trivial wrapping (e.g. markdown fences).
    """
    text = raw_text.strip()
    if text.startswith("```"):
        # Strip markdown fences if present.
        lines = text.splitlines()
        # Drop first and last fence-like lines
        if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def suggest_workflow(
    goal_description: str,
    data_context: Optional[Dict[str, Any]] = None,
    existing_workflow: Optional[Dict[str, Any]] = None,
    cases_context: Optional[Dict[str, Any]] = None,
    llm_client: Optional[LLMClient] = None,
) -> ComposerResult:
    """Ask an LLM to propose a workflow JSON and validate it."""
    client = _ensure_client(llm_client)

    user_parts: List[str] = [
        "User goal:\n",
        goal_description,
    ]
    if data_context:
        user_parts.append("\nData context (paths, formats, notes):\n")
        user_parts.append(json.dumps(data_context, indent=2, default=str))
    if existing_workflow:
        user_parts.append("\nExisting workflow to refine (JSON):\n")
        user_parts.append(json.dumps(existing_workflow, indent=2, default=str))
    if cases_context:
        user_parts.append("\nVerification-case context (JSON):\n")
        user_parts.append(json.dumps(cases_context, indent=2, default=str))

    user_prompt = "\n".join(user_parts)

    system_prompt = _build_workflow_system_prompt()
    raw = client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

    parsed = _parse_llm_json(raw)
    if parsed is None:
        vr = ValidationResult(
            valid=False,
            issues=[
                # type: ignore[arg-type]
                # (Construction is fine; ValidationIssue comes from schema_utils)
                # We avoid importing ValidationIssue directly here to keep the
                # public surface small; callers can inspect `issues` as needed.
            ],
        )
        return ComposerResult(ok=False, data=None, validation=vr, raw_text=raw)

    validation = validate_workflow_dict(parsed)
    return ComposerResult(ok=validation.valid, data=parsed, validation=validation, raw_text=raw)


def suggest_verification_cases(
    goal_description: str,
    signals_available: Optional[Dict[str, Any]] = None,
    existing_cases: Optional[Dict[str, Any]] = None,
    llm_client: Optional[LLMClient] = None,
) -> ComposerResult:
    """Ask an LLM to propose verification-case JSON and validate it."""
    client = _ensure_client(llm_client)

    user_parts: List[str] = [
        "User goal for verification cases:\n",
        goal_description,
    ]
    if signals_available:
        user_parts.append("\nSignals / datapoints available:\n")
        user_parts.append(json.dumps(signals_available, indent=2, default=str))
    if existing_cases:
        user_parts.append("\nExisting verification-case suite to refine (JSON):\n")
        user_parts.append(json.dumps(existing_cases, indent=2, default=str))

    user_prompt = "\n".join(user_parts)

    system_prompt = _build_cases_system_prompt()
    raw = client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

    parsed = _parse_llm_json(raw)
    if parsed is None:
        vr = ValidationResult(
            valid=False,
            issues=[],
        )
        return ComposerResult(ok=False, data=None, validation=vr, raw_text=raw)

    validation = validate_case_suite_dict(parsed)
    return ComposerResult(ok=validation.valid, data=parsed, validation=validation, raw_text=raw)


__all__ = [
    "ComposerResult",
    "suggest_workflow",
    "suggest_verification_cases",
]

