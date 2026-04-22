# LABELING.md: canonical forms for training labels

The 30 labeled rows in `data/train_labels.jsonl` follow the rules below. Apply
the same rules when thinking about what your `extract()` function should return.
The hidden test set is labeled with these same rules.

If something is ambiguous in a posting and this file does not adjudicate it,
prefer the most literal reading of the posting text.

---

## `title`

- Use the exact title as written in the posting, with normal title casing
  preserved ("Senior Software Engineer", not "senior software engineer").
- **Drop any modifier that follows a comma or em-dash.** These are team/org
  qualifiers, not the role itself.
  - "Staff Backend Engineer, Payments" → `"Staff Backend Engineer"`
  - "Tech Lead, Backend" → `"Tech Lead"`
  - "Senior Software Engineer — Platform" → `"Senior Software Engineer"`
- Keep Roman numerals and levels that are part of the title itself: "QA
  Engineer II" stays `"QA Engineer II"`.
- If the posting puts the title in the heading along with the company
  (e.g. "Frontend Developer — LondonTech Ltd."), the title is just the role
  part: `"Frontend Developer"`.

## `company`

- Exact string as written, including suffixes like `Ltd.`, `Inc.`, `Corp`.
- `"LondonTech Ltd."`: keep the period.

## `location`

Canonical forms, by region:

| Posting says | Label |
|---|---|
| US city | `"City, ST"`, e.g. `"San Francisco, CA"` |
| UK city | `"City, UK"`, e.g. `"London, UK"`, `"Manchester, UK"` |
| Canadian city | `"City, Province, Canada"`, e.g. `"Toronto, ON, Canada"` |
| Other international city | `"City, Country"`, e.g. `"Berlin, Germany"`, `"Paris, France"` |
| City-state or single-country city | `"City"`, e.g. `"Singapore"` |
| Fully remote, specific region | `"Remote (region)"`, e.g. `"Remote (US)"`, `"Remote (US/Canada)"` |
| Fully remote, any geography | `"Remote (worldwide)"` |

For hybrid roles, the location is the office city, not "hybrid". The
hybrid-ness goes into `is_remote` (which is `false` for hybrid).

## `is_remote`

- `true`: fully remote, even if restricted to a region ("Remote (US)" is
  still `true`).
- `false`: on-site, or hybrid with any required in-office days. Hybrid is
  explicitly **not** remote.

## `experience_level`

The enum is `"entry" | "mid" | "senior" | "unknown"`. Apply in priority
order, stopping at the first rule that matches. These four rules are
**exhaustive**. There is no "specialized-role" or "scope-signals-seniority"
exception. If the title doesn't carry a seniority word and the posting
doesn't disclaim years, the year count alone decides.

1. Posting **explicitly disclaims** experience as a signal ("we care about
   impact, not years of experience"; "rate negotiable based on experience,
   no annual figure published") → `unknown`. Do **not** use `unknown` just
   because the posting is silent about years. Fall through to the next
   rule in that case.
2. Title contains **Senior / Staff / Principal / Lead / Head / Director** →
   `senior`, regardless of years.
3. Title contains **Intern / Junior / Associate / Entry** → `entry`,
   regardless of years.
4. Otherwise, use stated years: **0–1 → entry**, **2–4 → mid**, **5+ → senior**.

## `salary_min`, `salary_max`, `salary_currency`

- **Salary fields represent annual salary only.** If the posting only gives
  an hourly or contract rate, set all three fields (`salary_min`,
  `salary_max`, `salary_currency`) to `null`. Do **not** extrapolate hourly
  to annual.
- If the posting is a flat number ("Flat comp: $160,000"), set
  `salary_min = salary_max = 160000`.
- If the posting withholds salary ("disclosed later", "competitive"), set
  all three to `null`.
- `salary_currency` is one of `"USD" | "EUR" | "GBP" | "other"`. CAD, AUD,
  SGD, etc. all label as `"other"`, **but only when the annual figure
  itself is in that currency.** If salary fields are `null` (withheld, or
  hourly-only), `salary_currency` is also `null`.

## `required_skills`

- **Include only named technical skills, tools, languages, frameworks,
  platforms, or methodologies.** A "named" skill is one the posting would
  bullet-list: a discrete noun phrase. Descriptions of duties ("managing a
  team of 5+") are **not** named skills and should not be included.
- Do not infer. If the posting says "you'll build dashboards," do not add
  `"data visualization"`.
- Soft skills (communication, leadership, management) are excluded even if
  the posting mentions them.
- Normalize to **lowercase**, preserving internal punctuation:
  - `"python"`, `"aws"`, `"kubernetes"`
  - `"c++"`, `"node.js"`, `"a/b testing"`
  - `"ios sdk"` (not `"ios"`; use the exact form the posting names)
  - `"typescript"`, `"swiftui"`, `"next.js"`
- Multi-word skills keep their spaces and slashes: `"a/b testing"`,
  `"distributed systems"`, `"distributed training"`, `"offensive security"`.
- "Nice to have" / "Bonus" skills are **excluded**; include only required ones.
- Return a list (order does not matter for scoring; set-F1 is used).

## `years_experience_min`

- `"N+ years"` → `N` (e.g. "5+ years" → `5`).
- `"M–N years"` → `M` (e.g. "1–3 years" → `1`).
- `"no prior experience required"` → `0`.
- Posting explicitly disclaims years ("we care about impact, not years";
  "rate negotiable based on experience") → `null`.
- Posting simply silent on years → `null`.
