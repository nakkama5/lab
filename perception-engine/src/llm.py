"""LLM wrapper around the Anthropic SDK."""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Optional

import anthropic

# Model constants — override via environment
MODEL_OBSERVE = os.environ.get("MODEL_OBSERVE", "claude-sonnet-4-6")
MODEL_DERIVE = os.environ.get("MODEL_DERIVE", "claude-sonnet-4-6")
MODEL_RESEARCH = os.environ.get("MODEL_RESEARCH", "claude-haiku-4-5-20251001")
MODEL_SYNTHESIZE = os.environ.get("MODEL_SYNTHESIZE", "claude-sonnet-4-6")
MODEL_DISTILL = os.environ.get("MODEL_DISTILL", "claude-sonnet-4-6")

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


def _log_usage(model: str, usage: Any) -> None:
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    # Rough cost estimates (per million tokens)
    cost_map = {
        "claude-sonnet-4-6": (3.0, 15.0),
        "claude-haiku-4-5-20251001": (0.25, 1.25),
    }
    in_rate, out_rate = cost_map.get(model, (3.0, 15.0))
    cost = (input_tokens * in_rate + output_tokens * out_rate) / 1_000_000
    print(
        f"[llm] model={model} in={input_tokens} out={output_tokens} cost=${cost:.4f}",
        file=sys.stderr,
    )


def call(
    system: str,
    user: str,
    model: str = MODEL_OBSERVE,
    max_tokens: int = 8192,
    tools: Optional[list[dict]] = None,
) -> str:
    """Call the model, return text content as a string."""
    client = _get_client()
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    if tools:
        kwargs["tools"] = tools

    response = client.messages.create(**kwargs)
    _log_usage(model, response.usage)

    # Extract text from content blocks
    text_parts = []
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts)


def call_with_web_search(
    system: str,
    user: str,
    model: str = MODEL_RESEARCH,
    max_tokens: int = 8192,
) -> str:
    """Call model with web_search tool enabled. Returns concatenated text."""
    client = _get_client()
    web_search_tool = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5,
    }
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=[web_search_tool],
    )
    _log_usage(model, response.usage)

    # Filter text blocks by type, not position
    text_parts = []
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts)


def parse_json(raw: str) -> Any:
    """Strip markdown fences, extract first JSON object or array, parse it."""
    # Strip ```json ... ``` fences
    raw = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Find first {...} or [...] block
    for pattern in (r"(\{[\s\S]*\})", r"(\[[\s\S]*\])"):
        match = re.search(pattern, raw)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Could not parse JSON from response. Raw (first 200 chars): {raw[:200]}")


def call_json(
    system: str,
    user: str,
    model: str = MODEL_OBSERVE,
    max_tokens: int = 8192,
    retries: int = 2,
) -> Any:
    """Call model expecting JSON, with retry on parse error."""
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            raw = call(system, user, model=model, max_tokens=max_tokens)
            return parse_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
            print(f"[llm] JSON parse attempt {attempt + 1} failed: {e}", file=sys.stderr)
    raise ValueError(f"Failed to parse JSON after {retries + 1} attempts: {last_error}")


def call_json_with_web_search(
    system: str,
    user: str,
    model: str = MODEL_RESEARCH,
    max_tokens: int = 8192,
    retries: int = 2,
) -> Any:
    """Call model with web search expecting JSON, with retry on parse error."""
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            raw = call_with_web_search(system, user, model=model, max_tokens=max_tokens)
            return parse_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
            print(f"[llm] JSON parse attempt {attempt + 1} failed: {e}", file=sys.stderr)
    raise ValueError(f"Failed to parse JSON after {retries + 1} attempts: {last_error}")
