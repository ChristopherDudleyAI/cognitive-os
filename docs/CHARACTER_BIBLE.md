# Cognitive OS — Demo Character Bible & Transcript Generation Rules
### Canonical source-of-truth for all fictional legal demo data

---

## GOVERNANCE — READ FIRST

This file is the source of truth for every fictional judge, attorney, firm, and rule used to generate Cognitive OS demo transcripts. It exists for two practical reasons Christopher has stated:

1. **Cross-session consistency.** Any conversation, starting cold, can write a new transcript that fits everything already built.
2. **Rebuilding after a wipe.** Testing an ingestion or extraction change means wiping the database and re-ingesting. The transcripts in `demo_data/` and this file are what survive that. The database is disposable; these are not.

**Rules for this file:**

1. **Prefer reading it to editing it.** It only does its job if a session can trust it without re-deriving everything.
2. **It may be corrected when it is wrong about itself.** Christopher's instruction: *"you can make changes to the bible to work best."* If the spec is internally inconsistent — a roster that cannot produce the posture mix it also demands — fix it here rather than writing transcripts that quietly miss the target. Say what changed and why, in the same edit.
3. **Never silently alter an established character's tendencies.** A character change that would contradict transcripts already written is a re-ingest decision, not an in-conversation edit. A change that only affects transcripts not yet written is fine — note it under that character.
4. **Where this file and the measured data disagree, find out which is wrong before changing either.** Both have been wrong. The `favored_neither` guidance below exists because the corpus drifted; the Kimball roster was rebalanced because the spec's own arithmetic did not close.
5. **If a transcript would contradict an established fact here** — a canonical name, a judge's signature rule, a case already written — the bible wins. Fix the transcript.

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

**`favored_neither` is the exception, not the safe default. Target 10%, roughly one ruling in ten.** This rule exists because the corpus drifted badly without it: measured across two dockets, `favored_neither` ran at 18% and 23% while `favored_defendant` came in 13 and 15 points *under* target on the same transcripts. The cause is a writing habit, not a tagging error — hearings were being padded with scheduling matters, joint extensions, and briefing-deadline housekeeping, which are genuinely neutral and genuinely worthless as evidence. They cost a directional ruling every time they appear.

Reserve it for rulings that truly have no winner: a jointly-requested continuance, a courtroom logistics matter. **A contested ruling always has a winner** — if both sides argued it, one of them lost, and it gets a directional tag. Cap it at one per transcript, and prefer zero.

**Budget each transcript at four or five directional rulings.** Fewer than four and the hearing is too thin to establish anything; more than six and one transcript dominates the judge's profile. Write real disputes, not filler.

**Check the docket arithmetic before writing, not after.** A judge's posture mix is the sum of their cases, so a case that is fine on its own can still push the docket off target. Multiply out first:

> Kimball wants ~50% `favored_defendant` across ~10 cases at ~4 directional rulings each — about 20 of 40 rulings. His four written cases hold 6. So the remaining six cases need roughly 14, which means running about 2-to-1 defence. Only counsel designed to *win* can supply that.

This is what caught the roster problem: for a defence-leaning judge, defence counsel written to lose produce `favored_plaintiff` rulings, so a roster of mostly-losing attorneys cannot add up to a defence lean no matter how each individual case is written. **A judge's party lean and their counsel roster's win rates are the same number seen twice.** If they disagree, the roster is wrong.

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

**Where her written docket actually stands (measured 2026-08-24): 46p / 30d / 23n against a 45/45/10 target.** Plaintiff is right; defence is 15 points light and neutral is 13 heavy. Her roster does not need rebalancing the way Kimball's did — most of that gap is the `favored_neither` padding described in the global rules, and converting those rulings into real contested ones largely closes it. Her four remaining cases should run about **2 plaintiff / 3 defendant each, with no neutrals**, which lands the docket near 20p / 20d / 4n.

Her counsel are written to lose their signature fight and win elsewhere, and the "elsewhere" has been under-written. Cross genuinely wins discovery craft; Whitfield genuinely wins on the merits; Anand's briefs genuinely persuade on the papers. Those wins are in character and they are where her defence rulings come from.

### Opposing counsel (defense — Reynolds docket only)
1. **Helena Cross** — aggressive commercial litigator, genuinely strong on discovery strategy, but overreaches in settlement posture and strong-arms. The overreach backfires specifically with Reynolds, who dislikes strong-arming. → wins discovery fights, loses when she overreaches.
2. **Gregory Whitfield** — methodical on the merits but under-prepared on procedural nuance. (Distinct from DeLuca: DeLuca fails to read the record; Whitfield knows the record but fumbles procedure.) → wins on merits when he has them, loses motions to sloppiness.
3. **Theodore Lange** — relies on boilerplate, templated briefs and generic damages models. Reynolds's anti-boilerplate skepticism cuts directly against him. → loses methodology and damages fights.
4. **Priya Anand** — superb written advocate, weak on her feet. Because Reynolds lets oral argument expand beyond the briefs, Anand gets caught flat-footed when argument goes past what she wrote. → strong on paper, loses live extensions.
5. **Brett Kowalski** — discovery gamesmanship and stonewalling. Reynolds's sharpest trigger. → sanctions against him; rulings favor the other side.

### Cases already written
- **Brightwater Logistics v. Sumner Freight Systems** (Discovery Hearing, 2025-CH-01188) — Soto v. Kowalski. Motion to compel granted (favored_plaintiff), Rule 37 fees awarded (favored_plaintiff), deemed-admissions request denied as disproportionate to the harm (favored_defendant), motion to quash overbroad non-party subpoena to Coleman Terminal Services granted (favored_defendant). Establishes her stonewalling trigger and her remedy-matches-harm rule.
- **Ashfield Millwork v. Calloway Development Group** (Motion Hearing, 2025-CH-00934) — Okafor v. Lange. Motion to exclude plaintiff's damages expert Ferris denied (favored_plaintiff), plaintiff's own boilerplate reputational-harm figure excluded (favored_defendant), plaintiff's limine motion on mitigation denied (favored_defendant), Section 4.2 construed to require mutual agreement on course of dealing (favored_plaintiff), late response brief excused for lack of prejudice (favored_neither). Anti-boilerplate rule applied symmetrically to both sides in the same hearing.
- **Meridian Textile Group v. Corbin Holdings** (Discovery and Motion Hearing, 2025-CH-01402) — Okafor v. Cross. Protective order limiting an overbroad 30(b)(6) notice granted (favored_defendant), work-product objection split by date of creation (favored_plaintiff in part), motion to strike requests for admission denied after a settlement threat aimed at the principals personally (favored_plaintiff). Establishes that Cross wins on genuine discovery craft and loses when she strong-arms.
- **Kesterline Industrial Supply v. Aldridge Manufacturing** (Summary Judgment, 2025-CH-01055) — Soto v. Whitfield. SJ granted on a failed condition precedent proved by plaintiff's own logs (favored_defendant), late limine motion heard anyway for want of prejudice but with a pattern warning (favored_defendant), limine motion denied on the merits (favored_plaintiff), quarterly measurement construed on course of performance (favored_defendant). Whitfield wins on merits, is warned on procedure — his designed profile.
- **Brightwater Logistics v. Sumner Freight Systems** (Sanctions Hearing, 2025-CH-01188) — Soto v. Kowalski. **Second hearing in the same matter as case 1.** Post-order destruction of routing logs: sanctions granted, full fees, adverse inference, referral (favored_plaintiff); request to strike the answer denied as disproportionate (favored_defendant); expert deadline extension granted in part, fifteen days not thirty (favored_defendant). Escalation from the warning issued in the first hearing.
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

**Rebalanced 2026-08-24.** The original roster had three of five attorneys designed to lose. Defence losses are `favored_plaintiff` rulings, so that roster could not produce the ~50% `favored_defendant` this docket calls for — the two halves of the spec contradicted each other, and the written transcripts came in at 37% defence as a result. Wu and Hoffman are now net winners. Neither change contradicts a case already written: Wu's one appearance was already split, and Hoffman had none. Target per-case posture is given for each, in directional rulings.

1. **Margaret Stahl** — elite doctrinal defense advocate. Builds clean records and wins summary judgment frequently under Kimball's rigor. **The strong adversary.** Her favored_defendant wins are CORRECT and consistent — not deviations — which itself tests whether the engine correctly reads a defense-lean rather than flagging it as contradiction. → **~1 plaintiff / 3 defendant per case.**
2. **Janet Wu** — professional-liability specialist, genuinely strong on standard-of-care doctrine and expert qualification. She knows the like-specialty rule cold and uses it to strike plaintiff experts. Loses where the record shows a real factual dispute she cannot argue away. → **~1 plaintiff / 3 defendant per case.**
3. **Carl Hoffman** — aggressive employer-side advocate with solid doctrinal instincts, who wins on clean records and then overplays credibility and sympathy arguments in the close cases where Kimball ignores both. His losses are concentrated in the contested calls, not the clear ones. → **~1 plaintiff / 3 defendant per case.**
4. **Daniel Reyes** — competent, but over-reaches on summary judgment where the facts ARE genuinely disputed. Kimball denies those. → produces favored_plaintiff "deviations" from the defense lean. **~3 plaintiff / 1 defendant per case.**
5. **Owen Fitzgerald** — boilerplate, sloppy employer defense. Fails to build clean doctrinal records and loses the contested motions. His client still wins counts that fail as a matter of law, because Kimball follows the doctrine regardless of who briefed it — that is the whole of his character. → **~3 plaintiff / 1 defendant per case.**

**Why this closes.** Four cases written (6 defence rulings) plus six remaining at Stahl 1, Wu 1, Hoffman 2, Reyes 1, Fitzgerald 1 gives roughly 10 plaintiff and 14 defendant to come — a docket near 17p / 20d / 4n, which is the 40/50/10 target. Fitzgerald is owed a second appearance in case 11; every other counsel lands in the 2–4 range.

### Cases already written
- **Radcliffe v. Nordwell Logistics** (Summary Judgment, 2025-L-004188) — Okafor v. Stahl. ADEA SJ granted at the pretext step (favored_defendant), plaintiff cross-motion on retaliation denied (favored_defendant), retaliation count expressly preserved because nobody moved on it (favored_plaintiff). Establishes step-by-step McDonnell Douglas and his "I decided no such thing" disclaimer about fairness.
- **Ferraro v. Brightline Staffing** (Summary Judgment, 2025-L-003921) — Soto v. Reyes. FMLA interference and retaliation SJ both denied on a genuinely disputed record (favored_plaintiff), expert qualification challenge denied (favored_plaintiff), after-acquired evidence barred on liability but admitted on damages (split). Reyes over-reaching on SJ where facts are disputed — his designed profile.
- **Delacroix v. Ashmont Wealth Advisors** (Motions Hearing, 2025-L-004510) — Pace v. Wu. Standard-of-care expert barred for lack of like-specialty qualification (favored_defendant), SJ denied as premature against the scheduling order (favored_plaintiff), disciplinary file compelled in part, sustained finding in and closed complaint out (split). Establishes strict expert qualification in professional liability.
- **Osei v. Cranmore Industrial Group** (Summary Judgment, 2025-L-004033) — Soto v. Stahl. Both Title VII counts SJ granted (favored_defendant, twice), unsupported affirmative defense struck (favored_plaintiff), joint briefing extension granted (favored_neither). Stahl second appearance; establishes his rejection of "totality of the circumstances" as an argument.

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
