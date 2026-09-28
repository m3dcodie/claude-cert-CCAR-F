"""
Task Statement 1.7 — Session state, resumption, and forking.

Pattern:  `--resume <session-name>` continues a specific NAMED prior
          conversation. `fork_session` branches an independent copy off a
          shared baseline so two approaches can be explored without one
          contaminating the other. When resuming after code changed, the
          agent must be TOLD what changed — it has no way to know on its
          own. When prior tool results are stale, starting fresh with an
          injected structured summary beats resuming (a resumed session
          will otherwise reason from outdated tool output).
Avoids:   resuming a long session and assuming it "knows" about file edits
          made outside the conversation; blindly resuming when the cheaper,
          more reliable move is a fresh session seeded with a summary.
"""

import copy


class Session:
    def __init__(self, name: str, history: list[dict]):
        self.name = name
        self.history = history

    def inform_of_changes(self, changed_files: list[str]) -> None:
        """
        Resuming does NOT auto-detect file changes. The caller must inject
        this explicitly so the agent re-analyzes only what's needed instead
        of redoing a full exploration from scratch.
        """
        note = {
            "role": "user",
            "content": (
                f"Note: since we last spoke, these files changed and should "
                f"be re-analyzed (everything else you found earlier still "
                f"holds): {changed_files}"
            ),
        }
        self.history.append(note)


class SessionStore:
    """Stand-in for Claude Code's --resume / fork_session mechanics."""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def start(self, name: str, initial_message: str) -> Session:
        session = Session(name, [{"role": "user", "content": initial_message}])
        self._sessions[name] = session
        return session

    def resume(self, name: str) -> Session:
        if name not in self._sessions:
            raise KeyError(f"No session named {name!r} to resume.")
        return self._sessions[name]

    def fork(self, source_name: str, new_name: str) -> Session:
        """
        Independent branch from a shared baseline: the fork gets a COPY of
        history at this point, then diverges — changes in one fork never
        affect the other or the original.
        """
        source = self.resume(source_name)
        forked_history = copy.deepcopy(source.history)
        forked = Session(new_name, forked_history)
        self._sessions[new_name] = forked
        return forked


def main():
    print("=" * 72)
    print("[MOCK] 1.7 — session resumption and forking semantics")
    print("=" * 72)

    store = SessionStore()

    # --- named resumption ---
    baseline = store.start(
        "refactor-analysis",
        "Analyze billing.py and auth.py for a refactor to remove duplicated validation logic.",
    )
    baseline.history.append(
        {"role": "assistant", "content": "Found 3 duplicated validation blocks across both files."}
    )
    print(f"Session '{baseline.name}' has {len(baseline.history)} turns after initial analysis.")

    # Simulate work happening outside the conversation (code changed).
    resumed = store.resume("refactor-analysis")
    resumed.inform_of_changes(["auth.py"])
    print(f"Resumed '{resumed.name}' -- last message: {resumed.history[-1]['content']}")

    # --- forking to compare two approaches from the SAME baseline ---
    fork_a = store.fork("refactor-analysis", "refactor-approach-shared-mixin")
    fork_b = store.fork("refactor-analysis", "refactor-approach-decorator")

    fork_a.history.append({"role": "assistant", "content": "Exploring a shared validation mixin class."})
    fork_b.history.append({"role": "assistant", "content": "Exploring a validation decorator instead."})

    print(f"\nfork 'shared-mixin' turns:  {len(fork_a.history)}")
    print(f"fork 'decorator' turns:     {len(fork_b.history)}")
    print("Both forks share the same first 2 turns (baseline) then diverge independently:")
    print(f"  fork_a[-1]: {fork_a.history[-1]['content']}")
    print(f"  fork_b[-1]: {fork_b.history[-1]['content']}")
    assert fork_a.history[0] == fork_b.history[0] == baseline.history[0]
    print("  (shared baseline confirmed identical across original + both forks)")


if __name__ == "__main__":
    main()
