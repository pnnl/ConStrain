"""
Introspection utilities for discovering workflow building blocks.

These helpers inspect the public ConStrain API and verification library to
produce a machine-readable catalog of:

- Callable methods that can be used in `MethodCall` workflow states.
- Available verification classes from the verification library, along with
  their metadata and datapoint requirements.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, asdict
from importlib import resources
from typing import Any, Dict, List, Optional

from constrain.api import (
    DataProcessing,
    Reporting,
    Verification,
    VerificationCase,
    VerificationLibrary,
)


@dataclass
class CallableParamInfo:
    name: str
    kind: str
    default: Any = inspect._empty
    annotation: Any = inspect._empty


@dataclass
class CallableInfo:
    qualified_name: str
    module: str
    owner: Optional[str]
    doc: Optional[str]
    params: List[CallableParamInfo]


@dataclass
class VerificationClassInfo:
    name: str
    description: Optional[str]
    datapoints: Optional[Any]
    raw: Dict[str, Any]


def _collect_class_callables(
    cls: type, *, prefix: Optional[str] = None
) -> List[CallableInfo]:
    """Collect public instance methods of a class as potential MethodCall targets."""
    callables: List[CallableInfo] = []
    for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        qualname = f"{cls.__module__}.{cls.__name__}.{name}"
        if prefix:
            qualname = f"{prefix}.{name}"

        sig = inspect.signature(member)
        params = []
        for p in sig.parameters.values():
            params.append(
                CallableParamInfo(
                    name=p.name,
                    kind=str(p.kind),
                    default=p.default,
                    annotation=p.annotation,
                )
            )

        callables.append(
            CallableInfo(
                qualified_name=qualname,
                module=cls.__module__,
                owner=cls.__name__,
                doc=inspect.getdoc(member),
                params=params,
            )
        )
    return callables


def list_workflow_callables() -> List[CallableInfo]:
    """Return a catalog of callables suitable for `MethodCall` workflow states.

    This currently includes instance methods on:
    - DataProcessing
    - VerificationCase
    - Verification
    - Reporting
    """
    catalog: List[CallableInfo] = []

    catalog.extend(_collect_class_callables(DataProcessing))
    catalog.extend(_collect_class_callables(VerificationCase))
    catalog.extend(_collect_class_callables(Verification))
    catalog.extend(_collect_class_callables(Reporting))

    return catalog


def list_verification_classes() -> List[VerificationClassInfo]:
    """Return a catalog of verification classes from the verification library.

    Uses the VerificationLibrary API to load `schema/library.json` and extract
    information that is helpful when composing verification cases, such as:

    - `verification_class` name
    - descriptions
    - required datapoints, if available
    """
    # Locate the built-in verification library JSON using package resources.
    try:
        lib_resource = resources.files("constrain.schema").joinpath("library.json")
        lib_path = str(lib_resource)
    except Exception:
        # Fallback to a relative path; if this fails, VerificationLibrary will log errors.
        lib_path = "constrain/schema/library.json"

    vlib = VerificationLibrary(lib_path)

    # If instantiation failed, there may be no lib_items attribute.
    if not hasattr(vlib, "lib_items"):
        return []

    results: List[VerificationClassInfo] = []
    for lib_name, lib_def in vlib.lib_items.items():
        # Only expose items that have a corresponding Python class loaded into globals(),
        # i.e., items that are actually executable.
        if lib_name not in globals():
            continue

        # The JSON schema uses description_* keys; the key name itself serves as the class identifier.
        description = (
            lib_def.get("description_brief")
            or lib_def.get("description_detailed")
            or lib_def.get("description_index")
        )
        datapoints = lib_def.get("description_datapoints") or lib_def.get("datapoints")

        results.append(
            VerificationClassInfo(
                name=lib_name,
                description=description,
                datapoints=datapoints,
                raw=lib_def,
            )
        )

    return results


def as_serializable(obj: Any) -> Any:
    """Convert dataclasses from this module into plain dicts/lists."""
    if isinstance(obj, list):
        return [as_serializable(x) for x in obj]
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return obj


__all__ = [
    "CallableParamInfo",
    "CallableInfo",
    "VerificationClassInfo",
    "list_workflow_callables",
    "list_verification_classes",
    "as_serializable",
]
