"""
AI-related helpers for ConStrain.

This package provides:
- LLM client abstraction (`LLMClient`, `LLMConfig`)
- Utilities for schema-backed validation of workflows and verification cases
- Introspection helpers for available workflow building blocks
- High-level AI-assisted workflow and verification-case composer functions
"""

from .llm_client import LLMClient, LLMConfig, HTTPJSONLLMClient, get_default_llm_client

__all__ = [
    "LLMClient",
    "LLMConfig",
    "HTTPJSONLLMClient",
    "get_default_llm_client",
]
