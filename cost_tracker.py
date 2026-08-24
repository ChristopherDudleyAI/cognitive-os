"""Running total of what this project has spent on API calls.

Every paid call records its ACTUAL token usage from the API response
rather than an estimate. The Anthropic API returns exact input, output,
and cache token counts on every response, so there is no reason to guess.

The ledger is an append-only JSONL file at the repo root, and it is
tracked in git on purpose — see the note on LEDGER_PATH. Each line is one
call. Nothing here ever deletes or rewrites
a line — a spend record that can be edited is not a spend record.

Usage:

    from cost_tracker import record_usage, print_report

    response = client.messages.create(...)
    record_usage(model, response.usage, operation="extraction",
                 detail="Reynolds_01")

    print_report()          # running total, grouped by model and operation
"""

import json
import os
from datetime import datetime, timezone

# Deliberately at the repo root, not under data/. data/ is gitignored and
# gets wiped on database resets — which already destroyed two demo
# transcripts. A spend record that disappears when you clear the database
# is not a record. It contains no secrets: token counts and dollar amounts.
LEDGER_PATH = "api_spend.jsonl"

# USD per million tokens, (input, output). Source: the model pricing table
# in the claude-api reference, checked 2026-08-22. Update deliberately —
# a stale rate here produces a confidently wrong total, which is worse
# than no total at all.
PRICING = {
    "claude-fable-5":    (10.00, 50.00),
    "claude-mythos-5":   (10.00, 50.00),
    "claude-opus-5":      (5.00, 25.00),
    "claude-opus-4-8":    (5.00, 25.00),
    "claude-opus-4-7":    (5.00, 25.00),
    "claude-opus-4-6":    (5.00, 25.00),
    "claude-sonnet-5":    (3.00, 15.00),
    "claude-sonnet-4-6":  (3.00, 15.00),
    "claude-haiku-4-5":   (1.00,  5.00),
}

# Cache tokens are priced relative to the input rate: a 5-minute write
# costs ~1.25x, a read costs ~0.1x.
CACHE_WRITE_MULTIPLIER = 1.25
CACHE_READ_MULTIPLIER = 0.10


def price_for(model: str):
    # Tolerate a provider prefix (Bedrock uses "anthropic.claude-...").
    key = model.split(".")[-1] if "." in model else model
    return PRICING.get(key)


def compute_cost(model: str, input_tokens: int, output_tokens: int,
                 cache_write_tokens: int = 0,
                 cache_read_tokens: int = 0):
    """Returns cost in USD, or None if the model has no known rate."""
    rates = price_for(model)
    if rates is None:
        return None
    in_rate, out_rate = rates
    return (
        input_tokens * in_rate
        + cache_write_tokens * in_rate * CACHE_WRITE_MULTIPLIER
        + cache_read_tokens * in_rate * CACHE_READ_MULTIPLIER
        + output_tokens * out_rate
    ) / 1_000_000


def record_usage(model: str, usage, operation: str = "unknown",
                 detail: str = "", estimated: bool = False):
    """Append one call to the ledger. `usage` is the response.usage object
    (or any object/dict carrying the same token fields)."""

    def field(name):
        if usage is None:
            return 0
        if isinstance(usage, dict):
            return usage.get(name) or 0
        return getattr(usage, name, 0) or 0

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model,
        "operation": operation,
        "detail": detail,
        "input_tokens": field("input_tokens"),
        "output_tokens": field("output_tokens"),
        "cache_write_tokens": field("cache_creation_input_tokens"),
        "cache_read_tokens": field("cache_read_input_tokens"),
        "estimated": estimated,
    }
    entry["cost_usd"] = compute_cost(
        model, entry["input_tokens"], entry["output_tokens"],
        entry["cache_write_tokens"], entry["cache_read_tokens"],
    )

    parent = os.path.dirname(LEDGER_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def record_estimate(model: str, cost_usd: float, operation: str,
                    detail: str = "", calls: int = 1):
    """For spend that happened before the ledger existed, or any call whose
    real usage was not captured. Flagged so it is never confused with a
    measured figure."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model, "operation": operation, "detail": detail,
        "input_tokens": 0, "output_tokens": 0,
        "cache_write_tokens": 0, "cache_read_tokens": 0,
        "estimated": True, "calls": calls, "cost_usd": cost_usd,
    }
    parent = os.path.dirname(LEDGER_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def totals():
    rows = load_ledger()
    measured = sum(r["cost_usd"] or 0 for r in rows if not r.get("estimated"))
    estimated = sum(r["cost_usd"] or 0 for r in rows if r.get("estimated"))
    calls = sum(r.get("calls", 1) for r in rows)
    unpriced = sum(1 for r in rows if r["cost_usd"] is None)
    return {
        "calls": calls,
        "measured_usd": measured,
        "estimated_usd": estimated,
        "total_usd": measured + estimated,
        "unpriced_calls": unpriced,
    }


def format_report() -> str:
    rows = load_ledger()
    if not rows:
        return "API spend: no calls recorded yet."

    by_model, by_op = {}, {}
    for r in rows:
        c = r["cost_usd"] or 0
        n = r.get("calls", 1)
        m = by_model.setdefault(r["model"], {"calls": 0, "usd": 0.0})
        m["calls"] += n
        m["usd"] += c
        o = by_op.setdefault(r["operation"], {"calls": 0, "usd": 0.0})
        o["calls"] += n
        o["usd"] += c

    t = totals()
    lines = ["API SPEND", "=" * 52]
    lines.append(f"{'by model':<26}{'calls':>7}{'USD':>12}")
    for k, v in sorted(by_model.items(), key=lambda x: -x[1]["usd"]):
        lines.append(f"  {k:<24}{v['calls']:>7}{v['usd']:>12.4f}")
    lines.append("")
    lines.append(f"{'by operation':<26}{'calls':>7}{'USD':>12}")
    for k, v in sorted(by_op.items(), key=lambda x: -x[1]["usd"]):
        lines.append(f"  {k:<24}{v['calls']:>7}{v['usd']:>12.4f}")
    lines.append("=" * 52)
    lines.append(f"  {'measured':<24}{'':>7}{t['measured_usd']:>12.4f}")
    if t["estimated_usd"]:
        lines.append(f"  {'estimated (pre-ledger)':<24}{'':>7}{t['estimated_usd']:>12.4f}")
    lines.append(f"  {'RUNNING TOTAL':<24}{t['calls']:>7}{t['total_usd']:>12.4f}")
    if t["unpriced_calls"]:
        lines.append(f"  ({t['unpriced_calls']} call(s) on a model with no known rate — not counted)")
    return "\n".join(lines)


def print_report():
    print(format_report())


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print_report()
