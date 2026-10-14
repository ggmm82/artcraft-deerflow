"""Compatibility helpers for the ChatGPT Codex Responses endpoint."""

from typing import Any


def modernize_codex_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Add fields emitted by current Codex CLI releases.

    DeerFlow's pinned provider predates these fields.  The ChatGPT Codex
    endpoint validates the private Responses payload more strictly than the
    public API and otherwise answers with a generic HTTP 400.
    """
    compatible = dict(payload)
    compatible.setdefault("tool_choice", "auto")
    compatible.setdefault("parallel_tool_calls", bool(compatible.get("tools")))
    compatible.setdefault("include", ["reasoning.encrypted_content"])
    return compatible
