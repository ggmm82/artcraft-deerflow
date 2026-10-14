"""DeerFlow Codex provider adapted to the current Codex CLI wire format."""

import httpx

from deerflow.models.openai_codex_provider import CodexChatModel

from .codex_compat import modernize_codex_payload


class StudioCodexChatModel(CodexChatModel):
    """Keep DeerFlow's provider while matching current Codex request fields."""

    def _stream_response(self, headers: dict, payload: dict) -> dict:
        try:
            return super()._stream_response(headers, modernize_codex_payload(payload))
        except httpx.HTTPStatusError as exc:
            # The upstream exception hides the response body, which made all
            # endpoint validation failures look like an unexplained HTTP 400.
            try:
                detail = exc.response.text.strip()
            except (httpx.ResponseNotRead, httpx.StreamClosed):
                detail = ""
            suffix = f": {detail[:2000]}" if detail else ""
            raise RuntimeError(f"Codex API HTTP {exc.response.status_code}{suffix}") from exc
