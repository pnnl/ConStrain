"""
Provider-agnostic LLM client abstraction used by AI helpers in ConStrain.

The goal of this module is to define a small, explicit contract for making
LLM calls, while keeping the concrete transport/provider configurable.

By default, `get_default_llm_client()` looks for the following environment
variables and, if they are present, configures an HTTP JSON client that
speaks a simple OpenAI-compatible chat API:

- `CONSTRAIN_LLM_API_BASE`  (e.g. https://api.openai.com/v1)
- `CONSTRAIN_LLM_API_KEY`
- `CONSTRAIN_LLM_MODEL`     (e.g. gpt-4.1, gpt-4.1-mini, etc.)

If any of these are missing, `get_default_llm_client()` returns `None` and
callers are expected to handle the absence of an LLM (e.g. by disabling
AI-assisted features or requiring explicit configuration).

The HTTP client is intentionally minimal and avoids adding new third-party
dependencies by using the Python standard library (`urllib`).
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional


@dataclass
class LLMConfig:
    """Configuration for an LLM endpoint."""

    api_base: str
    api_key: str
    model: str
    timeout: float = 30.0


class LLMClient(ABC):
    """Abstract interface for language model clients.

    Implementations are responsible for turning a (system, user) prompt pair
    into a single text completion, with optional sampling controls.
    """

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a single text completion.

        Implementations should raise a descriptive Exception on transport or
        API errors so callers can surface meaningful feedback to users.
        """


class HTTPJSONLLMClient(LLMClient):
    """Minimal HTTP JSON client for OpenAI-style chat APIs.

    This client assumes an API that accepts POST requests to:

        {api_base}/chat/completions

    with a JSON body of the form:

        {
          "model": "<model-name>",
          "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
          ],
          "temperature": 0.2,
          "max_tokens": 512
        }

    and returns a JSON response with `choices[0].message.content`.

    This matches common OpenAI-compatible providers and many self-hosted
    gateways. For non-compatible providers, implement a custom `LLMClient`
    subclass instead.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

        # Reuse default SSL context but keep it overridable via env if needed.
        self._ssl_context = ssl.create_default_context()

    @property
    def _chat_url(self) -> str:
        base = self.config.api_base.rstrip("/")
        # Common OpenAI-compatible path; callers can point api_base directly
        # at /chat/completions if their provider differs.
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"

    def _build_request_body(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": float(temperature),
        }
        if max_tokens is not None:
            body["max_tokens"] = int(max_tokens)
        return body

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        body = self._build_request_body(
            system_prompt, user_prompt, temperature, max_tokens
        )
        data = json.dumps(body).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            # Many providers use Bearer tokens; if a provider needs a
            # different header, a custom client should be implemented.
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        request = urllib.request.Request(
            self._chat_url,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request, timeout=self.config.timeout, context=self._ssl_context
            ) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            # Try to surface any JSON error message if present.
            msg = f"LLM HTTP error {e.code}"
            try:
                detail_raw = e.read().decode("utf-8")
                detail_json = json.loads(detail_raw)
                msg = f"{msg}: {detail_json}"
            except Exception:
                # Fall back to default message
                pass
            raise RuntimeError(msg) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to reach LLM endpoint: {e}") from e

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM returned non-JSON response: {raw}") from e

        # OpenAI-compatible shape: choices[0].message.content
        try:
            choices: Iterable[Dict[str, Any]] = parsed["choices"]
            first = next(iter(choices))
            message = first.get("message") or {}
            content = message.get("content")
        except Exception as e:
            raise RuntimeError(
                f"Unexpected LLM response format, expected 'choices[0].message.content': {parsed}"
            ) from e

        if not isinstance(content, str):
            raise RuntimeError(f"LLM response content is not a string: {content!r}")

        return content


def get_default_llm_client() -> Optional[LLMClient]:
    """Create an `LLMClient` from environment variables, if possible.

    Returns:
        HTTPJSONLLMClient instance if configuration is complete; otherwise
        `None`, indicating that AI-assisted features should be considered
        unavailable until configured.
    """

    api_base = os.getenv("CONSTRAIN_LLM_API_BASE")
    api_key = os.getenv("CONSTRAIN_LLM_API_KEY", "")
    model = os.getenv("CONSTRAIN_LLM_MODEL")

    if not api_base or not model:
        # Intentionally silent: callers can decide whether to warn the user.
        return None

    timeout_str = os.getenv("CONSTRAIN_LLM_TIMEOUT", "")
    try:
        timeout = float(timeout_str) if timeout_str else 30.0
    except ValueError:
        timeout = 30.0

    config = LLMConfig(api_base=api_base, api_key=api_key, model=model, timeout=timeout)
    return HTTPJSONLLMClient(config)


__all__ = ["LLMClient", "LLMConfig", "HTTPJSONLLMClient", "get_default_llm_client"]
