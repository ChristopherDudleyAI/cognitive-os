# Cognitive OS — Demo Character Bible & Transcript Generation Rules
### Canonical source-of-truth for all fictional legal demo data

---

## ⚠️ GOVERNANCE — READ FIRST

This file is the single source of truth for every fictional judge, attorney, firm, and rule used to generate Cognitive OS demo transcripts. It exists so any conversation can write a new transcript that stays perfectly consistent with everything already built.

**Rules for this file:**
1. **It is READ-ONLY in normal use.** Future conversations read it to write consistent transcripts. They do not edit it casually.
2. **It changes only in two situations:** (a) when ALL demo data is being re-ingested from scratch, or (b) when deliberately ADDING new characters/judges. Christopher has stated he would rather re-ingest fresh data than make piecemeal "corrections" that risk introducing inconsistency.
3. **Never silently alter an established character's tendencies or a judge's rule.** If a character needs to change, that is a full-reset decision, made explicitly, not an in-conversation edit.
4. **If a transcript you are writing would contradict anything here, stop.** The bible wins. Re-read it and adjust the transcript, not the bible.

---

## GLOBAL RULES (apply to EVERY transcript)

**Proceedings:** Civil only. Bench proceedings only — depositions, motion hearings, bench trials, discovery hearings. NO jury trials. NO criminal cases. (Reason: a judge's documented rulings are predictable and writable; jury reactions are not, and the product's job is to demonstrate per-judge pattern recognition.)

**The firm:** All cases are viewed from the perspective of **Hollis & Park LLP**, a plaintiff's-side litigation boutique. The firm always represents the plaintiff / claimant / the party bringing the claim. Therefore:
- Hollis & Park attorneys are always the **source_attorney** ("our side").
- The other side's lawyers are always **opposing_counsel** (defense).

**Posture tags (the #3 fix — critical):** Every memory describing a judicial ruling must carry exactly one posture tag, judged by EFFECT not verb:
- `favored_plaintiff` — outcome benefited the plaintiff (plaintiff's motion granted, OR defendant's objection/motion denied)
- `favored_defendant` — outcome benefited the defendant (defendant's motion granted, OR plaintiff's objection/motion denied)
- `favored_neither` — purely procedural / administrative / neutral ruling
- "Objection sustained" favors whoever raised it; "objection overruled" favors the opposing party. Always ask: who benefited?

**Don't make every ruling go the same way.** Each judge has a dominant lean, but a believable, demoable docket needs genuine opposite-posture rulings too (a competent opposing counsel winning on real merits; a rule that happens to help the defense). Without real deviations, the confidence/deviation engine has nothing to detect. Each judge profile below states the intended posture mix.

**Attorney isolation (cross-judge rule):** Each opposing counsel appears in front of **only ONE judge** for now. Do not put a Caldwell defense attorney in a Reynolds case, etc. (Reason: the pattern engine clusters opposing-counsel rulings by ruling context but not by which judge ruled, so the same attorney before two judges could produce a false "deviation." Cross-judge attorney tracking is a deliberate later experiment, not part of the base dataset.) The firm's OWN attorneys (Hollis & Park) MAY appear before any judge — they are not deviation-tracked, so this is safe and realistic.

**Recurrence:** Each opposing counsel should appear in roughly 2–4 of their judge's ~10 cases, so each one accumulates enough rulings to form a real, confidence-backed pattern. A one-off attorney produces no usable per-attorney intelligence.

**Canonical naming (the #2 fix):** Use the EXACT name strings below, every time, in every transcript. The system normalizes whitespace but cannot merge "Hon. Marcus T. Caldwell" with "Caldwell." Pick the canonical string and never vary it. Judges are stored by bare name (e.g., "Marcus T. Caldwell"). In transcript dialogue, "THE COURT" is fine for the judge's lines; just make the judge's full name appear in the caption/header so extraction captures it.

---

## CONTROLLED TAG VOCABULARY (what the extractor clusters on)

Transcripts should be written so these are inferable. The extractor applies them; consistency in the writing makes them land cleanly.

- **Ruling type:** objection_sustained, objection_overruled, motion_granted, motion_denied, evidence_admitted, evidence_excluded, sanctions_issued, discovery_ordered
- **Legal basis:** foundation_objection, speculation_objection, hearsay_objection, assumes_facts_objection, mischaracterization_objection, relevance_objection, daubert_standard, spoliation, privilege_claim, deadline_violation, standard_of_care, causation
- **Proceeding:** deposition_proceeding, motion_hearing, trial_proceeding, summary_judgment, motion_in_limine, discovery_hearing
- **Strategy:** examination_technique, objection_strategy, motion_strategy, argument_framing, witness_impeachment, document_strategy, deadline_management
- **Outcome:** strategy_succeeded, strategy_failed, strategy_partial, tactic_succeeded, tactic_failed
- **Posture:** favored_plaintiff, favored_defendant, favored_neither

Memory types: matter, client, precedent, partner_judgment, operational.
Extraction categories: case_intelligence, attorney_strategy, judge_intelligence, opposing_counsel, witness_intelligence, client_intelligence, fact_pattern, procedural, general.

---

## THE FIRM — HOLLIS & PARK LLP (source attorneys, may appear before any judge)

- **Diane Okafor** — lead trial attorney. Meticulous, reads the full record, anticipates the judge. The firm's strongest courtroom advocate.
- **Raymond Soto** — senior associate. Strong legal researcher, builds clean records and citations. Reliable on motions.
- **Lillian Pace** — partner. Negotiation and settlement strength; strategic, picks fights worth having.

---

# JUDGE 1 — HON. MARCUS T. CALDWELL
**Canonical name string: `Marcus T. Caldwell`**
**Court:** Superior Court of Fulton County, Georgia
**Docket:** Medical malpractice & personal injury

### Posture signature: PARTY LEAN (plaintiff)
Caldwell is skeptical of institutional defendants and protective of injured plaintiffs — but he applies his rules symmetrically and will rule for the defense when the rule genuinely points that way. **Intended mix: ~70% favored_plaintiff, ~20% favored_defendant (legitimate), ~10% favored_neither.**

### Decision framework (his consistent, recurring rules — keep these stable across all his cases)
- **Reads the entire record himself** before any hearing; verifies cited materials; catches mischaracterizations from the bench.
- **Deadlines are absolute.** A missed disclosure/discovery deadline, without pre-deadline notice to BOTH opposing counsel AND the clerk, means exclusion. No cure, no exceptions.
- **Oral argument is strictly limited to grounds raised in the written motion papers.** "A footnote is not an argument." Terminates hearings promptly once he rules; no reconsideration.
- **Daubert requires DUAL foundation:** clinical/professional experience PLUS specific published-guideline citation. An expert with both survives; a methodology-gap challenge fails when citations are present. Extrapolation disputes are cross-examination weight, not gatekeeping.
- **Spoliation:** an internal incident report that names records by name triggers a litigation-hold duty immediately, even pre-suit. "Routine retention policy" is no defense. Remedy is an adverse-inference instruction (standard form), not answer-striking (reserved for egregious conduct).
- **Treating physicians** may testify to medical knowledge tied to their own procedure (treating-surgeon-as-fact-witness objection overruled).
- **Speculation objections overruled** when a supervisor/professional is questioned about their own systems or expertise.
- **Medical board materials:** adjudicated findings admissible on notice; pending and dismissed complaints excluded ("prove nothing at this stage"). Firm rule — this one sometimes helps the defense.
- **Style:** Socratic, sequential yes/no questioning to force concessions and cut through evasive advocacy.

### Opposing counsel (defense — Caldwell docket only)
1. **Frank DeLuca** — chronic under-preparation. Misses deadlines, doesn't read the record, dresses cross-examination points up as Daubert gaps. Loses on procedure. → mostly favored_plaintiff against him.
2. **William Tate** — aggressive, corner-cutting. Document and discovery problems; drew spoliation sanctions. Reckless. → favored_plaintiff against him, tactic_failed.
3. **Howard Brennan** — genuinely competent defense. Picks winnable fights and prepares them. **The primary source of LEGITIMATE favored_defendant rulings** on Caldwell's docket. Sometimes beats the plaintiff lean on real merits.
4. **Caroline Yates** — methodical Daubert specialist. Her challenges succeed ONLY when the plaintiff's expert genuinely lacks dual foundation; otherwise they fail. → occasional favored_defendant on Daubert, else favored_plaintiff.
5. **Gerald Voss** — institutional/hospital defense. Leans on "routine policy" and procedural defenses Caldwell rejects. Loses spoliation and discovery fights. → favored_plaintiff against him.

### Cases already written (do not duplicate or contradict)
- **Hayes v. Riverside Medical Center** (Motion Hearing, 2025) — Okafor v. DeLuca. Daubert denied (favored_plaintiff), spoliation sanctions granted (favored_plaintiff), pending Board complaint excluded (favored_defendant), late rebuttal expert excluded (favored_plaintiff). Patient Thomas Hayes; Dr. Aaron Prentice and Riverside Medical Center as defendants.

---

# JUDGE 2 — HON. PATRICIA A. REYNOLDS
**Canonical name string: `Patricia A. Reynolds`**
**Court:** Davidson County (Nashville), Tennessee — Chancery/Circuit
**Docket:** Contract & commercial disputes

### Posture signature: CONDUCT LEAN (good-faith actor) — NO party lean
This is the deliberate CONTRAST to Caldwell. Reynolds has no inherent plaintiff/defendant preference. Instead her rulings lean toward whichever party acted in good faith and against gamesmanship or boilerplate, **cluster by cluster.** On a discovery-gamesmanship cluster she favors the non-stonewaller; on a boilerplate-damages cluster she favors the challenger of the boilerplate. **Intended mix: roughly balanced on party (~45/45/10), but each ruling cluster has a clear CONDUCT-driven direction.** This tests whether the engine can learn a non-party pattern.

### Decision framework (her consistent rules)
- **Weighs actual prejudice case-by-case** rather than applying bright-line rules (the direct opposite of Caldwell). A late filing with a good-faith explanation and no real prejudice to the other side gets leniency; the same lateness paired with gamesmanship gets hammered.
- **Punishes discovery gamesmanship and stonewalling hard** — sanctions, adverse rulings. This is her sharpest trigger.
- **Skeptical of boilerplate/templated damages models.** Demands methodology tied to the specific deal and the specific loss, not a generic formula.
- **Allows oral argument to expand beyond the four corners of the briefs** if it's responsive to something opposing counsel raised (opposite of Caldwell).
- **Tolerant of procedural informality** — disfavors form-over-substance objections.
- **Contract interpretation:** where language is ambiguous, looks to course of dealing and commercial context, not just the four corners.
- **Settlement strong-arming / bad-faith negotiation tactics earn her disfavor** and color how she views that party's other positions.

### Opposing counsel (defense — Reynolds docket only)
1. **Helena Cross** — aggressive commercial litigator, genuinely strong on discovery strategy, but overreaches in settlement posture and strong-arms. The overreach backfires specifically with Reynolds, who dislikes strong-arming. → wins discovery fights, loses when she overreaches.
2. **Gregory Whitfield** — methodical on the merits but under-prepared on procedural nuance. (Distinct from DeLuca: DeLuca fails to read the record; Whitfield knows the record but fumbles procedure.) → wins on merits when he has them, loses motions to sloppiness.
3. **Theodore Lange** — relies on boilerplate, templated briefs and generic damages models. Reynolds's anti-boilerplate skepticism cuts directly against him. → loses methodology and damages fights.
4. **Priya Anand** — superb written advocate, weak on her feet. Because Reynolds lets oral argument expand beyond the briefs, Anand gets caught flat-footed when argument goes past what she wrote. → strong on paper, loses live extensions.
5. **Brett Kowalski** — discovery gamesmanship and stonewalling. Reynolds's sharpest trigger. → sanctions against him; rulings favor the other side.

### Cases already written
- **Brightwater Logistics v. Sumner Freight Systems** (Discovery Hearing, 2025-CH-01188) — Soto v. Kowalski. Motion to compel granted (favored_plaintiff), Rule 37 fees awarded (favored_plaintiff), deemed-admissions request denied as disproportionate to the harm (favored_defendant), motion to quash overbroad non-party subpoena to Coleman Terminal Services granted (favored_defendant). Establishes her stonewalling trigger and her remedy-matches-harm rule.
- **Ashfield Millwork v. Calloway Development Group** (Motion Hearing, 2025-CH-00934) — Okafor v. Lange. Motion to exclude plaintiff's damages expert Ferris denied (favored_plaintiff), plaintiff's own boilerplate reputational-harm figure excluded (favored_defendant), plaintiff's limine motion on mitigation denied (favored_defendant), Section 4.2 construed to require mutual agreement on course of dealing (favored_plaintiff), late response brief excused for lack of prejudice (favored_neither). Anti-boilerplate rule applied symmetrically to both sides in the same hearing.
- **Vantage Point Analytics v. Hartwell Capital Partners** (Summary Judgment, 2025-CH-00602) — Pace v. Anand. Partial SJ on the exclusivity covenant denied after oral argument expanded past the briefs (favored_plaintiff), SJ on tortious interference granted on a thin record (favored_defendant), defense motion to exclude a coercive March 14th settlement letter denied (favored_plaintiff). Establishes the oral-argument-expansion rule and her disfavor for settlement strong-arming.

---

# JUDGE 3 — HON. ROBERT D. KIMBALL
**Canonical name string: `Robert D. Kimball`**
**Court:** Circuit Court of Cook County, Illinois
**Docket:** Employment & professional liability

### Posture signature: DOCTRINE LEAN (text & precedent)
The third distinct type. Kimball follows the text and the controlling precedent wherever they lead, unmoved by sympathy or equity from either side. Because rigorous summary-judgment and burden-shifting standards often favor employers with clean records, he **leans defendant on summary judgment specifically** — but this is correct doctrinal application, not bias, and he rules for plaintiffs readily when the record shows genuine disputes. **Intended mix: defense-leaning on SJ clusters (~60% favored_defendant there), more balanced elsewhere; overall roughly 50% favored_defendant, 40% favored_plaintiff, 10% favored_neither.** This is a deliberately more defense-weighted docket than Caldwell's, to test that the engine learns opposite per-judge leans.

### Decision framework (his consistent rules)
- **Rigorous summary judgment standard.** Grants when there is no genuine dispute of material fact; denies when material facts are genuinely disputed. Strictly by the record, every time.
- **McDonnell Douglas burden-shifting applied step by step** in discrimination cases — prima facie case, legitimate non-discriminatory reason, pretext — and he holds each side to its step precisely.
- **Demands precise statutory/contractual text and controlling precedent.** Rejects "totality of the circumstances" hand-waving from either side.
- **Unmoved by sympathy or equity arguments.** A sympathetic plaintiff with a thin legal record loses; an unsympathetic employer with the law on its side wins.
- **Professional liability:** strict on expert qualification — standard-of-care opinion must come from a like-specialty expert.
- **Predictable IF you know the controlling law cold.** Rewards clean doctrinal records and precise citation; punishes vagueness.

### Opposing counsel (defense / employer-side — Kimball docket only)
1. **Margaret Stahl** — elite doctrinal defense advocate. Builds clean records and wins summary judgment frequently under Kimball's rigor. **The strong adversary.** Her favored_defendant wins are CORRECT and consistent — not deviations — which itself tests whether the engine correctly reads a defense-lean rather than flagging it as contradiction.
2. **Daniel Reyes** — competent, but occasionally over-reaches on summary judgment where the facts ARE genuinely disputed. Kimball denies those. → produces favored_plaintiff "deviations" from the defense lean.
3. **Owen Fitzgerald** — boilerplate, sloppy employer defense. Fails to build clean doctrinal records. → loses; favored_plaintiff against him.
4. **Janet Wu** — professional-liability specialist; strong on standard-of-care doctrine and expert qualification fights. Mixed results depending on the record.
5. **Carl Hoffman** — aggressive employer defense who leans on credibility and sympathy arguments Kimball ignores. → loses when the doctrine isn't on his side.

### Cases already written
- None yet. Kimball docket not started.

---

## QUICK CONTRAST TABLE (why the three judges are different on purpose)

- **Caldwell** — bias type: PARTY (pro-plaintiff). Triggered by: procedure & preparation. Rigid, bright-line. Reads the record. Lean: ~70% plaintiff.
- **Reynolds** — bias type: CONDUCT (pro good-faith actor). Triggered by: gamesmanship & boilerplate. Flexible, discretion-based. Weighs prejudice. Lean: balanced on party, directional per cluster.
- **Kimball** — bias type: DOCTRINE (pro text/precedent). Triggered by: weak legal records. Rigorous, textualist. Unmoved by sympathy. Lean: defense-leaning on SJ.

The point of the contrast: a real pattern engine should produce three visibly different judge profiles and three different posture distributions. If two judges' profiles start looking the same, something is wrong with the data or the engine.

---

## CHECKLIST BEFORE WRITING ANY NEW TRANSCRIPT
1. Civil, bench proceeding only.
2. Hollis & Park is plaintiff-side (source_attorney); the other side is opposing_counsel (defense).
3. Use only that judge's own opposing counsel, with their established tendencies — don't give a "loser" attorney an out-of-character win or a "strong" attorney an out-of-character loss.
4. Every ruling gets a posture tag by EFFECT. Include at least one genuine opposite-posture ruling where the judge's rules honestly point that way.
5. Keep the judge's signature rules consistent with this file.
6. Use exact canonical name strings.
7. Don't contradict a case already listed under "Cases already written."
