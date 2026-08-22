# Demo Data

Synthetic transcripts used to exercise the system. Everything here is **fictional** — invented judges, attorneys, firms, parties, and cases. No real client, matter, or privileged material appears anywhere in this directory, by design.

## Why these are versioned

They were not, and it cost us. Three Caldwell transcripts were written and ingested; when the database was reset, only one survived on disk. The other two exist now only as extracted memories that no longer exist either. Transcripts are the source material the entire demo rests on — losing one means rewriting it from scratch and hoping the new version stays consistent with everything the old one established.

## Structure

```
demo_data/
  caldwell/    Hon. Marcus T. Caldwell    — Fulton County, GA. Medical malpractice & personal injury.
  reynolds/    Hon. Patricia A. Reynolds  — Davidson County, TN. Contract & commercial.
  kimball/     Hon. Robert D. Kimball     — Cook County, IL. Employment & professional liability.
```

Naming: `<Judge>_<NN>_<Case>_<ProceedingType>.txt`

## Before writing a new transcript

**Read [`docs/CHARACTER_BIBLE.md`](../docs/CHARACTER_BIBLE.md) first.** It is the source of truth for every judge's decision framework, every attorney's tendencies, the canonical name strings, and the posture-mix targets. A transcript that contradicts it is a bug in the transcript, not in the bible.

Three rules cause the most damage when broken:

1. **Canonical names, exactly.** The system normalizes whitespace but cannot merge `Hon. Marcus T. Caldwell` with `Caldwell`. A name variant silently fragments that judge's entire evidence base.
2. **Defense counsel appear before one judge only.** Clustering groups opposing-counsel rulings by ruling context but not by which judge ruled, so the same attorney before two judges can manufacture a false deviation. Cross-judge tracking is a deliberate later experiment.
3. **Every ruling needs a genuine posture, judged by effect.** "Objection sustained" favors whoever raised it. And each judge needs real opposite-posture rulings — without honest deviations the confidence engine has nothing to detect and every pattern reads as unanimous.

## Current state

| Judge | Written | Target |
|---|---:|---:|
| Caldwell | 1 | ~10 |
| Reynolds | 3 | ~10 |
| Kimball | 0 | ~10 |

Each judge's opposing counsel should each appear in 2–4 of that judge's cases, so every attorney accumulates enough rulings to form a confidence-backed pattern. A one-off attorney produces no usable per-attorney intelligence.
