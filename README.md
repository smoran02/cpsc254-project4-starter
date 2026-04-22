# Project 4: Structured Data Extraction with LLMs

You will build an LLM-based extractor that pulls structured fields
(title, company, location, salary, required skills, etc.) out of
free-text job postings, and an evaluation harness that scores your
extractor against labeled data.

The canonical rules for how each field should be labeled are in
**`LABELING.md`**. Read that first — your extractor is graded against
those conventions.

## What you will implement

Complete the `TODO` markers in these two files:

1. **`extract.py`** — implement `extract(text: str) -> JobPosting`.
   It must call OpenAI's structured-output API with a strict JSON
   schema, validate the response against the `JobPosting` pydantic
   model, and perform exactly one repair retry on `ValidationError`
   before giving up. Iterate on `SYSTEM_PROMPT` here too.

2. **`eval.py`** — implement `score_field(field, predicted, expected)`.
   The scoring rules are documented in the function docstring. The
   rest of `eval.py` already orchestrates the run.

## Files you will create

- `iterations.md`: log at least 3 versions of your prompt/schema
  iterations with their scores. The required structure is in the
  "What goes in `iterations.md`" section below.
- `writeup.md` — 250–300 word error analysis referencing specific rows
  of `results.csv`.
- `results.csv` — written automatically when you run `eval.py`.

Also fill out **`AI_DISCLOSURE.md`** and remove its `TEMPLATE` sentinel
line. Missing or unfilled disclosure is a -10 point penalty.

## Files you must NOT modify

- `schema.py` — the pydantic model and `to_strict_schema` helper. The
  grader imports `JobPosting` from here.
- `check_submission.py` — the pre-flight check.
- `requirements.txt` — pinned dependency versions.
- `data/` — inputs and labels.
- The signatures of `extract(text)` and `score_field(field, predicted,
  expected)`. The grader imports and calls them with these exact
  signatures.
- The summary output block printed at the end of `eval.py`. The grader
  parses it by line format.

## AI policy

You may use AI assistants on this assignment. That includes ChatGPT,
Claude, Cursor, Copilot, local models, and agentic coding tools. They
are good at drafting a first pass of `score_field`, at argparse and
CSV boilerplate in `eval.py`, at explaining a stack trace, and at
being a sounding board while you iterate on your system prompt.

What this assignment is testing is your judgment about LLM systems:
which fields are hard to extract and why, what your current prompt is
getting wrong on which rows, and what change is likely to help. That
judgment shows up in `iterations.md` and `writeup.md`, and it is what
the grade is weighted toward. If you cannot speak to *why* your prompt
changed between v1 and v2, or *why* a specific row fails, the grade
will reflect that regardless of how clean the final code looks.

Treat AI like a collaborator you are learning from, not a replacement
for engaging with the problem. Disclose what you used and how in
`AI_DISCLOSURE.md`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the example env file and add your OpenAI API key:

```bash
cp .env.example .env
# then open .env and set OPENAI_API_KEY=sk-...
```

`extract.py` loads `.env` automatically via `python-dotenv`. `.env` is
gitignored. **Do NOT commit your API key.**

## Model and budget

Use `gpt-4o-mini`. Do not use `gpt-4o` or any larger model. Larger
models cost more and do not score better on this task. The bottleneck
is prompt and schema design, not model size.

You will need to add **$5 of credit** (OpenAI's minimum top-up) to your
account. You will spend well under $2 of it. The free tier's rate
limits are too tight for this assignment; adding credit moves you to a
higher tier and the rate-limit errors go away.

Per `extract()` call: ~400 input + ~150 output tokens ≈ $0.00015.
Per full eval run over the 30 training rows: ~$0.005.

Your final submission **must run live against the API**. Do not commit
pre-computed predictions.

## Development flow

1. **Read `LABELING.md`.** Your extractor is graded against these rules.
2. **Implement `score_field` in `eval.py`.** Write your own edge-case
   tests (empty-set F1, null-vs-null numeric, tolerance boundaries)
   before you submit — this function is graded against a hidden test
   file and fiddly cases fail silently.
3. **Implement `extract` in `extract.py`** with a simple first-attempt
   system prompt. The point of v1 is to have a runnable baseline, not
   to be good.
4. **Smoke test on the single example row** (one API call, surfaces
   wiring bugs without touching the training set):

   ```bash
   python eval.py --inputs data/example.jsonl --labels data/example_labels.jsonl
   ```

5. **Run the full eval on the 30-row training set:**

   ```bash
   python eval.py --inputs data/train.jsonl --labels data/train_labels.jsonl
   ```

   This prints the grader-parsed summary block and writes `results.csv`.

6. **Iterate on your system prompt.** Read the failing rows in
   `results.csv`, improve your prompt, re-run. Log each version in
   `iterations.md` with its score.

7. **Write `writeup.md`** — 250–300 word error analysis grounded in
   specific rows of `results.csv`.

8. **Fill out `AI_DISCLOSURE.md`** and remove the `TEMPLATE` sentinel
   line at the top.

## What goes in `iterations.md`

Consistent structure helps you see your own progress and helps the
grader read the file quickly. For each version, copy the block below
and fill it in. You need at least three versions, labeled `v1`, `v2`,
`v3`. Keep each version to roughly half a page.

### v<N>: <one-line summary of what this version is trying>

**Changed from previous:** What you changed and, in one sentence, why.
For `v1`, write "Baseline."

**Overall score:** XX.X% (from the `Overall score` line in the eval
summary, which is the graded number).

**Weakest fields:** `<field>` (XX.X%), `<field>` (XX.X%). Pull these
from the `Per-field accuracy` block printed by `eval.py`.

**What I saw in `results.csv`:** Two to four sentences grounded in
specific rows. Cite at least one row id and say what went wrong. For
example: 'row `007`: predicted `"Senior Engineer, Payments"` but label
is `"Senior Engineer"` because of the comma-suffix rule in
`LABELING.md`.'

**Hypothesis for next version:** One or two sentences on what you plan
to change and why you expect it to help. For your final version, it
is acceptable to write "no further changes planned" if you have run
out of ideas worth trying.

## Pre-flight check

During development (won't fail on missing output artifacts):

```bash
python check_submission.py
```

Right before you submit:

```bash
python check_submission.py --final
```

## Deliverables

- `extract.py` — implemented
- `eval.py` — implemented
- `schema.py` — unchanged
- `results.csv` — produced by the latest run of your eval
- `iterations.md`: at least 3 labeled versions (`v1`, `v2`, `v3`) each
  following the structure in "What goes in `iterations.md`"
- `writeup.md` — 250–300 word error analysis referencing `results.csv`
- `AI_DISCLOSURE.md` — filled out, `TEMPLATE` line removed
