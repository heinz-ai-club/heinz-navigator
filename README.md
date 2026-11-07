# Heinz Navigator

An AI assistant for Heinz College students. It answers questions about courses, policies, and career resources with a cited source for every answer, and checks what a student still needs for their degree.

A Heinz AI Club (HAIC) project, November 2026 to April 2027.

## The two features

| Group | Feature | Folder | Delivers |
| --- | --- | --- | --- |
| 1 | **Ask Heinz**: answers questions with a source for every answer | `ask/` | A cited-answer assistant with a before and after accuracy score |
| 2 | **Requirement Checker**: tells a student what they still need for their degree | `check/` | An agent tool that checks completed courses against degree requirements |

Members choose their group at kickoff (up to 6 per group). In spring, the Requirement Checker becomes a tool inside Ask Heinz, and both groups run the 20-student pilot together.

## How the repo is organized

```
heinz-navigator/
  app/            the web server and API (shared; changes need Trav's or the lead's review)
  interface/      the chat page both features plug into (shared)
  ask/            Group 1: Ask Heinz
  check/          Group 2: Requirement Checker
  eval/           shared question set and scoring script
  docs_corpus/    the collected Heinz documents both features answer from
  docs/           API contract, evaluation method, document collection, interface spec
  haic.py         the helper for calling AI models
```

The interface is already built. Each group only edits its own folder and replaces the placeholder in `service.py` with real AI. As long as each service returns the format in [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md), the interface keeps working.

## Get started

```bash
git clone https://github.com/heinz-ai-club/heinz-navigator.git
cd heinz-navigator
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then paste the Navigator key from your lead
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Both tabs work on day one with placeholder answers.

Run the tests before every pull request:

```bash
pytest
```

## Models

| Use | Model |
| --- | --- |
| Final answers, the requirement checker, evaluation runs, the pilot | `haiku` (Claude Haiku 5.5) |
| Quick experiments and debugging | `luna` (GPT-6 Luna) |

Haiku makes things up much less often, which matters for a tool students will trust. Luna is cheaper for testing.

## Measuring accuracy

The whole project is judged by one number: how often the assistant answers correctly, before and after our work. See [`docs/EVALUATION.md`](docs/EVALUATION.md).

## Rules

- Answers must come from public Heinz and CMU documents, with a source shown. No live web search.
- During the pilot, never store students' names or Andrew IDs with their questions.
- Read [`CONTRIBUTING.md`](CONTRIBUTING.md): pull requests only, keys only in `.env`.
