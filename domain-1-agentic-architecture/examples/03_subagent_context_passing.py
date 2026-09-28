"""
Task Statement 1.3 — Subagent invocation, explicit context passing, parallel spawning.

Pattern:  the Task tool spawns subagents (coordinator's allowedTools must
          include "Task"). Subagents do NOT auto-inherit the coordinator's
          conversation history — every piece of context they need must be
          written into their prompt explicitly. Structured data separates
          content from metadata (source URL, doc name, page number) so
          attribution survives being passed along. Parallel subagents are
          spawned by emitting multiple Task calls in a SINGLE coordinator
          turn, not sequential turns.
Avoids:   assuming a subagent "remembers" anything from earlier in the
          coordinator's conversation; passing a vague summary reference
          ("use the findings from before") instead of the actual content;
          spawning subagents one-by-one across separate turns when they
          could run in parallel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.mock_client import MockAnthropic, print_mock_banner  # noqa: E402


def web_search_finding() -> dict:
    # Structured: content separated from attribution metadata.
    return {
        "content": "The refund window was extended from 30 to 45 days in Q3.",
        "source_url": "https://intranet.example.com/policy/refunds",
        "retrieved_at": "2026-08-20",
    }


def build_synthesis_subagent_prompt(coordinator_query: str, prior_findings: list[dict]) -> str:
    """
    This is the entire context the subagent will ever see — nothing from the
    coordinator's own conversation history leaks in automatically. Every
    finding is included in full (not "see above"), and content/metadata are
    kept as separate structured fields so citations survive synthesis.
    """
    findings_block = "\n".join(
        f"- content: {f['content']}\n"
        f"  source_url: {f['source_url']}\n"
        f"  retrieved_at: {f['retrieved_at']}"
        for f in prior_findings
    )
    return (
        f"Research goal: {coordinator_query}\n\n"
        f"Quality criteria: synthesize the findings below into a short answer. "
        f"Preserve source_url attribution for every claim you make. Flag any "
        f"contradictions instead of silently picking one value.\n\n"
        f"Findings (complete, not summarized):\n{findings_block}\n"
    )


def spawn_parallel_task_calls(client: MockAnthropic, subagent_prompts: dict[str, str]) -> None:
    """
    Simulates emitting N Task tool_use blocks in a SINGLE assistant turn —
    this is what makes the subagents run in parallel rather than one Task
    call per turn (sequential).
    """
    client.queue_response(
        stop_reason="tool_use",
        tool_calls=[
            {"name": "Task", "input": {"subagent_type": name, "prompt": prompt}}
            for name, prompt in subagent_prompts.items()
        ],
    )
    response = client.messages.create(model="claude-sonnet-5", messages=[])
    task_calls = [b for b in response.content if b.type == "tool_use" and b.name == "Task"]
    print(f"Coordinator emitted {len(task_calls)} Task calls in ONE turn (parallel spawn):")
    for call in task_calls:
        print(f"  -> subagent_type={call.input['subagent_type']!r}")


def main():
    print_mock_banner("1.3", "explicit context passing + parallel Task spawning")

    finding = web_search_finding()
    prompt = build_synthesis_subagent_prompt(
        coordinator_query="What is the current refund policy window?",
        prior_findings=[finding],
    )
    print("Full prompt the synthesis subagent receives (its ONLY context):\n")
    print(prompt)

    client = MockAnthropic()
    spawn_parallel_task_calls(
        client,
        {
            "search-subagent": "Find 2026 refund policy updates.",
            "docs-subagent": "Check internal policy docs for refund window.",
        },
    )


if __name__ == "__main__":
    main()
