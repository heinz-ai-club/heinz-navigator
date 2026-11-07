# Interface spec (for the person building the shared shell)

The shell is the shared web app both groups plug into. It must work on day one with placeholder answers, so both groups can start on the AI immediately.

## Stack

- Python 3.11+
- FastAPI + Uvicorn for the server
- Pydantic v2 models matching `docs/API_CONTRACT.md` exactly
- One static page (`interface/static/index.html` + `app.js` + `style.css`), plain HTML, CSS, and JavaScript. No build step, no frameworks.
- pytest + httpx (FastAPI TestClient) for tests

Keep the code small and readable. Members range from strong engineers to people new to web apps.

## Files

```
app/__init__.py
app/main.py          FastAPI app: routes, static files, CORS off by default
app/schemas.py       Pydantic models: Source, AskRequest, AskResponse, CheckRequest, CheckResponse, Requirement, SatisfiedRequirement
ask/__init__.py
ask/service.py       def answer(question: str) -> AskResponse  (placeholder; Group 1 replaces)
check/__init__.py
check/service.py     def check(program, completed_courses, notes=None) -> CheckResponse  (placeholder; Group 2 replaces)
interface/static/index.html
interface/static/app.js
interface/static/style.css
eval/run_eval.py     evaluation runner (see docs/EVALUATION.md)
eval/results/.gitkeep
tests/test_api.py    contract tests
requirements.txt
haic.py              copied from the shared starter
.env.example
```

## Routes

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` | Serves `interface/static/index.html` |
| GET | `/static/*` | Static files |
| GET | `/api/health` | `{"status": "ok"}` |
| POST | `/api/ask` | Validates `AskRequest`, calls `ask.service.answer`, returns `AskResponse` |
| POST | `/api/check` | Validates `CheckRequest`, calls `check.service.check`, returns `CheckResponse` |

If a service raises an unexpected exception, return HTTP 500 with `{"detail": "Something went wrong. Please try again."}` and log the error. Never show stack traces or keys to the user.

## Placeholders

- `answer()` returns `status: "placeholder"`, an `answer` that says the feature is not built yet and repeats the question, one example Source pointing to `https://www.heinz.cmu.edu/`, and `model: null`.
- `check()` returns `status: "placeholder"`, echoes the program, lists the completed courses under one `satisfied` item named "Placeholder", one example `remaining` item, and `model: null`.
- Each placeholder file starts with a short comment telling the group what to replace and pointing to `docs/API_CONTRACT.md`.

## Page design

Minimal and dark, in the style of Apple and Tesla: lots of space, one accent color, system font stack, no clutter.

- Header: "Heinz Navigator" and a one-line subtitle.
- Two tabs: **Ask Heinz** and **Requirement Checker**.
- Ask Heinz tab: a text box, an Ask button (Enter submits, Shift+Enter is a new line), the answer, and below it a **Sources** list of clickable titles with the snippet in smaller text. Show a clear note when `status` is `no_answer` or `placeholder`.
- Requirement Checker tab: a program text field, a text area for completed courses (one per line or comma separated), a Check button, then two lists: **Done** (satisfied) and **Still needed** (remaining, with options), plus notes and sources.
- Loading state while waiting, and a friendly error message if the request fails.
- Footer note: "Answers come from public Heinz documents. Always confirm important decisions with your advisor. Please do not enter personal information."
- Works at phone width.
- Accessible: labels on inputs, keyboard usable, sufficient contrast.

## Tests (tests/test_api.py)

- `/api/health` returns ok.
- `/api/ask` with a valid question returns a response that validates as `AskResponse`.
- `/api/ask` with an empty question or more than 1,000 characters returns 422.
- `/api/check` with a valid request returns a response that validates as `CheckResponse`.
- `/api/check` with more than 60 courses returns 422.
- `/` returns HTML.
- No test may call a real AI model.

## Evaluation runner (eval/run_eval.py)

- Arguments: `--split dev|test|all` (default `dev`), `--label <name>` (required), `--feature ask|check|all` (default `all`), `--questions` path (default `eval/questions.csv`), `--no-judge` to skip the AI judge.
- Skips rows whose id starts with `EXAMPLE`.
- For `ask` rows, calls `ask.service.answer(question)`. For `check` rows, calls `check.service.check(program, completed_courses)` using the row's `program` and `completed_courses` columns (courses separated by semicolons), and gives the judge the formatted `satisfied`, `remaining`, and `notes` as the system answer.
- Judge: uses `haic.ask(..., model="luna")` with a short rubric prompt that returns JSON `{"label": "correct|partial|incorrect|correct_refusal", "citation_ok": true|false, "reason": "..."}`. Parse defensively; on bad JSON, label `needs_review`.
- Writes `eval/results/YYYY-MM-DD_<label>.csv` with: id, feature, category, question, verified_answer, system_answer, status, sources (joined), label, citation_ok, reason.
- Prints accuracy per feature and overall, using the formula in `docs/EVALUATION.md`.
- With placeholders in place, the runner should still complete and report 0% without crashing.
