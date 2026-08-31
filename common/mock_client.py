"""
Tiny offline stand-in for the Anthropic SDK client.

Every example script in this repo imports `MockAnthropic` instead of the real
`anthropic.Anthropic()` so the whole repo runs with no ANTHROPIC_API_KEY and no
network access. The shapes returned (`.content`, `.stop_reason`, block `.type` /
`.name` / `.input` / `.text`, `.usage`) mirror the real `messages.create()`
response closely enough that swapping in a real client is a one-line change:

    # from common.mock_client import MockAnthropic as Anthropic
    from anthropic import Anthropic

    client = Anthropic()   # picks up ANTHROPIC_API_KEY from env

Scripted responses are queued with `client.queue_response(...)`; each call to
`messages.create()` pops the next one. This keeps examples deterministic and
readable instead of reimplementing a real model.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentBlock:
    type: str  # "text" | "tool_use"
    text: str | None = None
    id: str | None = None
    name: str | None = None
    input: dict[str, Any] | None = None


@dataclass
class Message:
    content: list[ContentBlock]
    stop_reason: str  # "end_turn" | "tool_use" | "max_tokens"
    usage: dict[str, int] = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})
    role: str = "assistant"


class _Messages:
    def __init__(self, client: "MockAnthropic"):
        self._client = client

    def create(self, **kwargs) -> Message:
        self._client.calls.append(kwargs)
        if not self._client._queue:
            raise RuntimeError(
                "MockAnthropic: no queued response left. Call client.queue_response(...) "
                "before each expected messages.create() call."
            )
        return self._client._queue.pop(0)


class MockAnthropic:
    """Drop-in offline replacement for `anthropic.Anthropic()`."""

    _id_counter = itertools.count(1)

    def __init__(self, *_, **__):
        self.calls: list[dict[str, Any]] = []
        self._queue: list[Message] = []
        self.messages = _Messages(self)

    def queue_response(
        self,
        *,
        stop_reason: str,
        text: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> None:
        """Queue the next `messages.create()` response.

        tool_calls: list of {"name": ..., "input": {...}} — one ContentBlock
        per entry, each given a fresh synthetic tool_use id.
        """
        blocks: list[ContentBlock] = []
        if text:
            blocks.append(ContentBlock(type="text", text=text))
        for call in tool_calls or []:
            blocks.append(
                ContentBlock(
                    type="tool_use",
                    id=f"toolu_mock_{next(self._id_counter):03d}",
                    name=call["name"],
                    input=call["input"],
                )
            )
        self._queue.append(
            Message(content=blocks, stop_reason=stop_reason)
        )


def print_mock_banner(task_statement: str, pattern: str) -> None:
    print("=" * 72)
    print(f"[MOCK] {task_statement} — {pattern}")
    print("[MOCK] Running against MockAnthropic (no ANTHROPIC_API_KEY needed).")
    print("[MOCK] With a real key: `from anthropic import Anthropic` and drop")
    print("[MOCK] the .queue_response(...) calls — everything else is unchanged.")
    print("=" * 72)
