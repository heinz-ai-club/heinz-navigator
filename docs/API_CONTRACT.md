# API contract

This is the agreement between the interface and the two features. **Do not change these formats without agreement from both groups and the project lead**, because the interface, the evaluation script, and the spring merge all depend on them.

Each group implements one Python function. The web server wraps it in an HTTP endpoint.

## Shared: Source

```json
{
  "title": "MS in AI Systems Management Handbook 2026-27, Section 4.2",
  "url": "https://www.heinz.cmu.edu/...",
  "snippet": "Students must complete 96 units of core coursework..."
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `title` | string | yes | Human-readable name of the document and section |
| `url` | string | yes | Public link to the source page or PDF |
| `snippet` | string or null | no | The exact passage the answer relies on |

## Feature 1: Ask Heinz

Python: `ask/service.py`

```python
def answer(question: str) -> AskResponse
```

HTTP: `POST /api/ask`

Request:

```json
{ "question": "Can I take a course pass/fail in MS-AIM?" }
```

| Field | Type | Rules |
| --- | --- | --- |
| `question` | string | 1 to 1,000 characters |

Response:

```json
{
  "answer": "Yes, up to ...",
  "sources": [ { "title": "...", "url": "...", "snippet": "..." } ],
  "status": "ok",
  "model": "anthropic/claude-haiku-5.5"
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `answer` | string | The answer shown to the student |
| `sources` | list of Source | **At least one** when `status` is `ok` |
| `status` | `"ok"`, `"no_answer"`, or `"placeholder"` | `no_answer` when the documents do not answer the question; never guess |
| `model` | string or null | The model that produced the answer |

When the assistant cannot find an answer in the documents, it returns `status: "no_answer"` with a short message pointing the student to the right office. A wrong answer is worse than no answer.

## Feature 2: Requirement Checker

Python: `check/service.py`

```python
def check(program: str, completed_courses: list[str], notes: str | None = None) -> CheckResponse
```

HTTP: `POST /api/check`

Request:

```json
{
  "program": "MS-AIM",
  "completed_courses": ["95-888", "94-806"],
  "notes": "Starting spring 2027"
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `program` | string | Program code, e.g. `MS-AIM`, `MISM`, `MSPPM`. Group 2 decides which programs are supported |
| `completed_courses` | list of strings | CMU course numbers like `95-888`; 0 to 60 items |
| `notes` | string or null | Optional context from the student, up to 500 characters |

Response:

```json
{
  "program": "MS-AIM",
  "satisfied": [
    { "requirement": "Core: Programming", "courses": ["95-888"] }
  ],
  "remaining": [
    {
      "requirement": "Core: Statistics",
      "description": "One statistics course from the list below",
      "options": ["95-796", "90-711"]
    }
  ],
  "notes": "Electives are not checked yet.",
  "sources": [ { "title": "...", "url": "...", "snippet": null } ],
  "status": "ok",
  "model": "anthropic/claude-haiku-5.5"
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `program` | string | Echoes the request |
| `satisfied` | list of `{requirement, courses}` | Requirements already met and the courses that met them |
| `remaining` | list of `{requirement, description, options}` | What is still needed; `options` may be empty |
| `notes` | string or null | Caveats the student should know |
| `sources` | list of Source | The handbook pages the check used; at least one when `status` is `ok` |
| `status` | `"ok"`, `"unknown_program"`, or `"placeholder"` | `unknown_program` when the program is not supported yet |
| `model` | string or null | The model used, or null if the check is pure code |

## Errors

The server returns HTTP 422 automatically when a request breaks the field rules above. Services should not raise errors for normal "can't answer" cases; they return `no_answer` or `unknown_program` instead.

## Health check

`GET /api/health` returns `{"status": "ok"}`.
