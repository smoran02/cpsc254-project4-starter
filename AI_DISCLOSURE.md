# AI Disclosure

Fill this out honestly before you submit. See the AI policy in `README.md`
for the broader expectation; this file is where you describe, specifically,
how you used AI on your submission. Heavy use is fine if you can speak to
the judgment calls behind your `iterations.md` and `writeup.md`. Unfilled
or clearly sanitized disclosure is not. Delete the `TEMPLATE: edit before
submitting` line at the top once you have filled the sections in.

TEMPLATE: edit before submitting

## Tools used

List the AI assistants you used on this project (ChatGPT, Claude, Cursor,
Copilot, local model, etc.). Rough usage like "daily," "once for debugging,"
or "only for the writeup draft" is fine.

-

## Where AI helped

Briefly, in your own words, where did an assistant save you time or unblock you?
Name specific files or functions. Examples:

- "Used Claude to draft the skeleton of `score_field` for the list-F1 branch.
  I then modified the F1 denominator handling after my eval showed empty-set
  edge cases were scoring wrong."
- "Cursor autocomplete for argparse and csv writing in `eval.py`."

-

## Where you did the work yourself

Again in your own words. Which decisions, debugging sessions, or design
choices were driven by you rather than by the assistant? Examples:

- "Prompt iteration: ran the eval, read the failing rows, rewrote the
  system prompt four times. The assistant did not see `train_labels.jsonl`
  at any point."
- "`writeup.md` error analysis: all row references are rows I read myself."

-

## What you verified or pushed back on

Name at least one AI suggestion you verified (by running it, checking docs,
testing an edge case) or rejected/modified because it was wrong or a bad
fit. If you accepted every suggestion unchanged, say that instead. It is
useful signal. Examples:

- "Claude's first `score_field` numeric branch used `abs(p - e) < tol`,
  which crashes when either is `None`. I rewrote the null handling."
- "The assistant suggested adding a 'seniority' field to the schema.
  Rejected, since it is not in `LABELING.md` and would break the grader."

-

## Anything else

Optional. If you used AI in a way that felt borderline, say so. Honest
disclosure with a borderline case is fine; a sanitized disclosure that turns
out to be misleading is not.

-
