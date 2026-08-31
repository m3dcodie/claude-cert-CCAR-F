"""
Task Statement 4.5 — Batch processing strategy with the Message Batches API.

Pattern:  batch = ~50% cost savings, up to a 24h processing window, NO
          latency SLA, and NO mid-request tool calling. Appropriate for
          non-blocking, latency-tolerant work; wrong for a blocking
          pre-merge check. `custom_id` correlates each response back to its
          request, which is what makes partial-failure resubmission
          tractable. SLA math: if you need a guaranteed N-hour turnaround
          and batches can take up to 24h, submit frequently enough that
          the LATEST possible batch completion still beats the deadline.
Avoids:   using the batch API for a blocking workflow (pre-merge checks
          need synchronous, bounded latency); submitting once a day when
          the SLA requires tighter turnaround than one 24h window allows.
"""

from dataclasses import dataclass, field


@dataclass
class BatchRequest:
    custom_id: str
    document_id: str
    payload_size_tokens: int


@dataclass
class BatchResult:
    custom_id: str
    succeeded: bool
    error: str | None = None
    output: dict | None = None


def submit_batch(requests: list[BatchRequest], max_context_tokens: int = 100_000) -> list[BatchResult]:
    """
    Simulated batch processing — including a realistic failure mode
    (oversized document) that resubmission needs to handle.
    """
    results = []
    for req in requests:
        if req.payload_size_tokens > max_context_tokens:
            results.append(
                BatchResult(req.custom_id, succeeded=False, error="context_length_exceeded")
            )
        else:
            results.append(
                BatchResult(req.custom_id, succeeded=True, output={"summary": f"processed {req.document_id}"})
            )
    return results


def chunk_document(req: BatchRequest, chunk_size: int = 40_000) -> list[BatchRequest]:
    """Resubmission fix for context_length_exceeded: split into chunks."""
    n_chunks = -(-req.payload_size_tokens // chunk_size)  # ceil div
    return [
        BatchRequest(
            custom_id=f"{req.custom_id}-chunk{i}",
            document_id=f"{req.document_id} (chunk {i+1}/{n_chunks})",
            payload_size_tokens=min(chunk_size, req.payload_size_tokens - i * chunk_size),
        )
        for i in range(n_chunks)
    ]


def demo_when_to_use_batch():
    print("--- 4.5: matching API choice to latency requirements ---")
    workflows = [
        ("nightly test generation for 200 modules", True),
        ("weekly compliance audit report", True),
        ("pre-merge CI check blocking a PR", False),
        ("overnight document classification, 5,000 docs", True),
    ]
    for name, use_batch in workflows:
        api = "Batch API (non-blocking, 50% cheaper, up to 24h)" if use_batch else "Synchronous API (blocking, needs bounded latency)"
        print(f"  {name}: {api}")


def demo_sla_math():
    print("\n--- 4.5: submission cadence to guarantee an SLA ---")
    sla_hours = 30
    max_batch_window_hours = 24
    # Worst case: a document submitted right after a cadence tick waits
    # (cadence) + (up to 24h processing) before it's guaranteed done.
    # Solve for cadence such that cadence + 24 <= sla_hours.
    max_cadence_hours = sla_hours - max_batch_window_hours
    print(f"  SLA: {sla_hours}h. Batch max window: {max_batch_window_hours}h.")
    print(f"  -> must submit at least every {max_cadence_hours}h to guarantee the SLA in the worst case")
    assert max_cadence_hours == 6


def demo_partial_failure_resubmission():
    print("\n--- 4.5: custom_id correlation + resubmission of failures only ---")
    batch = [
        BatchRequest("req-1", "doc-A.pdf", payload_size_tokens=8_000),
        BatchRequest("req-2", "doc-B.pdf", payload_size_tokens=150_000),  # too big
        BatchRequest("req-3", "doc-C.pdf", payload_size_tokens=12_000),
    ]
    results = submit_batch(batch)
    for r in results:
        status = "OK" if r.succeeded else f"FAILED ({r.error})"
        print(f"  {r.custom_id}: {status}")

    failed = [r for r in results if not r.succeeded]
    print(f"\n  resubmitting only {len(failed)} failed request(s), by custom_id, with fixes:")
    original_by_id = {r.custom_id: r for r in batch}
    resubmit_batch = []
    for f in failed:
        original = original_by_id[f.custom_id]
        if f.error == "context_length_exceeded":
            chunks = chunk_document(original)
            resubmit_batch.extend(chunks)
            print(f"    {f.custom_id} -> chunked into {len(chunks)} sub-requests")

    resubmit_results = submit_batch(resubmit_batch)
    for r in resubmit_results:
        print(f"    {r.custom_id}: {'OK' if r.succeeded else 'FAILED'}")


def main():
    print("=" * 72)
    print("[MOCK] 4.5 — Message Batches API: when to use it, SLA math, resubmission")
    print("=" * 72)
    demo_when_to_use_batch()
    demo_sla_math()
    demo_partial_failure_resubmission()


if __name__ == "__main__":
    main()
