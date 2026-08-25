"""Check demo transcripts against the Character Bible before ingesting.

Ingestion costs money. Every rule checked here describes a mistake that
produces no error at ingest time and is expensive or impossible to undo
afterwards:

- A name variant fragments an entity's whole evidence base, silently,
  because the system normalizes whitespace but cannot merge "Kimball"
  with "Robert D. Kimball".
- An opposing counsel appearing before two judges manufactures false
  deviations, because clustering groups counsel rulings by ruling
  context and not by which judge ruled.
- A firm attorney written into the defence chair inverts attribution.
- A jury or criminal proceeding is outside the corpus by design.

Run from the project root:

    python tools/check_transcripts.py
    python tools/check_transcripts.py demo_data/kimball

The roster below mirrors docs/CHARACTER_BIBLE.md. The bible is
authoritative -- update both together. This script verifies that every
judge it knows about still appears in the bible, which catches the case
where the two have drifted apart, but it cannot tell you the bible has
changed in ways it does not know about.
"""
import os
import re
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BIBLE = 'docs/CHARACTER_BIBLE.md'

FIRM_ATTORNEYS = ['Diane Okafor', 'Raymond Soto', 'Lillian Pace']

JUDGES = {
    'caldwell': {
        'canonical': 'Marcus T. Caldwell',
        'counsel': ['Frank DeLuca', 'William Tate', 'Howard Brennan',
                    'Caroline Yates', 'Gerald Voss'],
    },
    'reynolds': {
        'canonical': 'Patricia A. Reynolds',
        'counsel': ['Helena Cross', 'Gregory Whitfield', 'Theodore Lange',
                    'Priya Anand', 'Brett Kowalski'],
    },
    'kimball': {
        'canonical': 'Robert D. Kimball',
        'counsel': ['Margaret Stahl', 'Daniel Reyes', 'Owen Fitzgerald',
                    'Janet Wu', 'Carl Hoffman'],
    },
}

# Phrases meaning the PROCEEDING itself is outside the corpus. A passing
# reference to what a jury would eventually do is fine and realistic --
# a motion heard from the bench in a case later tried to a jury is still
# a bench proceeding. Only flag language that makes this transcript a
# jury or criminal proceeding.
FORBIDDEN = [
    (r'\bvoir dire\b', 'jury selection'),
    (r'\bmembers of the jury\b', 'the court addressing a seated jury'),
    (r'\bthe jury (?:is|will be) (?:excused|dismissed|polled)\b',
     'a seated jury'),
    (r'\bjury trial\b(?! *(?:demand|waiver))', 'a jury trial proceeding'),
    (r'\bthe People of the State\b', 'criminal caption'),
    (r'\bindictment\b', 'criminal proceeding'),
    (r'\bdefendant is sentenced\b', 'criminal sentencing'),
]

# Language that describes THIS proceeding as a trial. In a transcript
# captioned as a hearing, that is the Reynolds_06 bug: a stray "this
# being a bench trial" caused 24 memories to be tagged trial_proceeding,
# which manufactured clusters that do not exist. Future references
# ("you will win at trial") are fine -- these patterns are present-tense
# and self-describing.
TRIAL_FRAMING = re.compile(
    r'\b(?:this|the present|today\'?s) (?:being a |is a )?'
    r'(?:bench )?trial\b'
    r'|\bwe are (?:here )?(?:at|in) trial\b'
    r'|\bthis trial\b',
    re.IGNORECASE
)

# Words that read as a ruling. A rough sanity check on whether a
# transcript has enough decided matters to be worth ingesting -- it
# counts words, not rulings, so treat it as a smell and not a measure.
RULING_RE = re.compile(
    r'\b(?:GRANTED|DENIED|DISMISSED|SUSTAINED|OVERRULED|STRICKEN)\b',
    re.IGNORECASE
)

errors = []
warnings = []


def problem(path, msg):
    errors.append(f"{path}: {msg}")


def warn(path, msg):
    warnings.append(f"{path}: {msg}")


# Cheap drift check: every judge this script knows must still be in the
# bible under the same canonical string.
if os.path.exists(BIBLE):
    bible_text = open(BIBLE, encoding='utf-8').read()
    for key, spec in JUDGES.items():
        if spec['canonical'] not in bible_text:
            errors.append(
                f"{BIBLE}: canonical name '{spec['canonical']}' is not in "
                f"the bible -- this script and the bible have drifted"
            )
        for counsel in spec['counsel']:
            if counsel not in bible_text:
                warnings.append(
                    f"{BIBLE}: '{counsel}' is in this script's {key} "
                    f"roster but not in the bible"
                )
else:
    warnings.append(f"{BIBLE} not found -- skipped the drift check")

roots = sys.argv[1:] or ['demo_data']
paths = []
for root in roots:
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if name.endswith('.txt'):
                paths.append(os.path.join(dirpath, name))

if not paths:
    sys.exit(f"No .txt transcripts found under {', '.join(roots)}")

print(f"Checking {len(paths)} transcript(s)\n")

for path in paths:
    text = open(path, encoding='utf-8').read()
    # Transcript captions are conventionally uppercase ("BEFORE THE
    # HONORABLE ROBERT D. KIMBALL", "DIANE OKAFOR, ESQ."), and the
    # extractor emits properly-cased names regardless. Case is therefore
    # not what breaks a join key -- a different name is. Match
    # case-insensitively; matching exactly flags every file in the
    # corpus and tells you nothing.
    lower = text.lower()
    folder = os.path.basename(os.path.dirname(path)).lower()
    spec = JUDGES.get(folder)

    if not spec:
        warn(path, f"folder '{folder}' matches no judge -- not checked")
        continue

    if spec['canonical'].lower() not in lower:
        problem(path, f"canonical judge name '{spec['canonical']}' "
                      f"does not appear")

    # A bare surname is fine in dialogue; what breaks the join key is a
    # near-miss variant of the full name, so look for the surname
    # preceded by an honorific but not matching the canonical string.
    surname = spec['canonical'].split()[-1].lower()
    for variant in re.findall(
        r'(?:honorable|hon\.|judge)\s+([\w.\- ]{0,40}?' +
        re.escape(surname) + r')', lower
    ):
        if variant.strip() != spec['canonical'].lower():
            problem(path, f"judge name variant '{variant.strip()}' -- "
                          f"must be '{spec['canonical']}'")

    # Counsel from another judge's docket breaks deviation detection.
    for other_key, other in JUDGES.items():
        if other_key == folder:
            continue
        for counsel in other['counsel']:
            if counsel.lower() in lower:
                problem(path, f"'{counsel}' belongs to the {other_key} "
                              f"docket and cannot appear here")

    present = [c for c in spec['counsel'] if c.lower() in lower]
    if not present:
        warn(path, "no rostered opposing counsel appears")
    elif len(present) > 1:
        warn(path, f"more than one opposing counsel appears: "
                   f"{', '.join(present)}")

    firm_present = [a for a in FIRM_ATTORNEYS if a.lower() in lower]
    if not firm_present:
        problem(path, "no Hollis & Park attorney appears -- the firm is "
                      "always plaintiff's counsel")

    # Attribution: the firm attorney must be introduced for the
    # plaintiff, the rostered counsel for the defence.
    for match in re.finditer(
        r'for the (plaintiff|defendants?):\s*([a-z.\- ]+),\s*esq',
        lower
    ):
        side = match.group(1).title()
        name = match.group(2).strip().title()
        is_firm = any(
            a.lower() == name.lower() for a in FIRM_ATTORNEYS
        )
        if side == 'Plaintiff' and not is_firm:
            problem(path, f"'{name}' appears for the plaintiff but is not "
                          f"a Hollis & Park attorney")
        if side.startswith('Defendant') and is_firm:
            problem(path, f"firm attorney '{name}' appears for the "
                          f"defence -- attribution is inverted")

    for pattern, label in FORBIDDEN:
        if re.search(pattern, text, re.IGNORECASE):
            problem(path, f"contains {label}")

    # Trial framing only matters if this transcript is not a trial.
    captioned_trial = 'trial' in os.path.basename(path).lower()
    if not captioned_trial:
        for match in TRIAL_FRAMING.finditer(text):
            problem(path, f"describes this proceeding as a trial "
                          f"(\"{match.group(0).strip()}\") but is "
                          f"captioned as a hearing -- this is how 24 "
                          f"memories got mis-tagged trial_proceeding")

    rulings = len(RULING_RE.findall(text))
    if rulings < 4:
        warn(path, f"only {rulings} ruling word(s) found -- the bible "
                   f"budgets 4-5 directional rulings per transcript")
    elif rulings > 14:
        warn(path, f"{rulings} ruling words -- unusually dense, check "
                   f"it is not dominating the judge's profile")

for w in warnings:
    print(f"  WARN  {w}")
if warnings:
    print()
for e in errors:
    print(f"  ERROR {e}")

print()
if errors:
    print(f"{len(errors)} error(s), {len(warnings)} warning(s). "
          f"Do not ingest until the errors are fixed.")
    sys.exit(1)
print(f"No errors. {len(warnings)} warning(s).")
