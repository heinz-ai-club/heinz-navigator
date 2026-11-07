# How we measure accuracy

Heinz Navigator is judged by one result: **how often it answers correctly, before and after our work.** Both groups use the same question set and the same scoring, so the numbers are comparable.

## The question set

File: `eval/questions.csv`

| Column | Meaning |
| --- | --- |
| `id` | Unique id, e.g. `Q001` |
| `feature` | `ask` or `check` |
| `category` | `courses`, `policies`, `careers`, or `requirements` |
| `question` | The question exactly as a student would ask it (for `check`, a one-line description of the case) |
| `program` | `check` rows only: program code, e.g. `MS-AIM` |
| `completed_courses` | `check` rows only: course numbers separated by semicolons, e.g. `95-888;94-806` |
| `verified_answer` | The correct answer, written by a member and checked by a second member |
| `source_url` | The public page that proves the answer |
| `split` | `dev` (use while building) or `test` (only for official scores) |
| `verified_by` | Initials of the two members who verified it |
| `date_verified` | YYYY-MM-DD |

Target: **about 100 questions** (roughly 70 `ask`, 30 `check`).

How to collect them:

1. Ask real Heinz students what they have looked up this semester (no names recorded).
2. Add common handbook questions: course rules, deadlines, credits, career services.
3. Each answer is written by one member and checked against the source by a second member.
4. Mark about **20%** of questions as `test`. Never look at test questions while improving the system, or the final score will be inflated.

Freeze the set as `v1` before the baseline run. If questions change later, save a new version (`questions_v2.csv`) and re-run the baseline on it, so before and after always use the same questions.

## Scoring each answer

| Label | Meaning |
| --- | --- |
| `correct` | Matches the verified answer on every fact that matters |
| `partial` | Right direction but missing or wrong on a detail |
| `incorrect` | Wrong, or invents something |
| `correct_refusal` | Returned `no_answer` for a question the documents truly do not answer |

Also record `citation_ok`: does at least one returned source actually support the answer?

**Accuracy** = (`correct` + `correct_refusal`) / total questions in the split.

## Running an evaluation

```bash
python eval/run_eval.py --split dev --label retrieval-v1
```

The script sends every question through the real service, asks an AI judge (GPT-6 Luna) to label each answer against the verified answer, and writes `eval/results/<date>_<label>.csv` plus a summary line.

The AI judge is fast but not perfect. For the official **baseline** (November) and **final** (April) scores, two members also review the judge's labels by hand and fix any mistakes.

## Schedule

| When | Run |
| --- | --- |
| End of November | Official baseline on `test` |
| Weekly | Any team member on `dev` |
| April | Official final score on `test`, reported at the showcase |
