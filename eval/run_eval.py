"""
Evaluation runner. See docs/EVALUATION.md for the method.

Examples:
    python eval/run_eval.py --split dev --label retrieval-v1
    python eval/run_eval.py --split all --feature check --label checker-v1 --no-judge

It sends every question through the real service, asks an AI judge (GPT-6 Luna)
to label each answer, writes eval/results/<date>_<label>.csv, and prints accuracy.
"""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

# Let this script import app/, ask/, check/ and haic.py from the repo root.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ask import service as ask_service  # noqa: E402
from check import service as check_service  # noqa: E402

LABELS = {"correct", "partial", "incorrect", "correct_refusal"}
RESULT_COLUMNS = [
    "id", "feature", "category", "question", "verified_answer", "system_answer",
    "status", "sources", "label", "citation_ok", "reason",
]

JUDGE_PROMPT = """You are grading an AI assistant for university students.

Question: {question}
Verified correct answer: {verified}
Assistant's answer: {system}
Assistant's status: {status}
Assistant's sources: {sources}

Label the assistant's answer with exactly one of:
- correct: matches the verified answer on every fact that matters
- partial: right direction but missing or wrong on a detail
- incorrect: wrong, or invents something
- correct_refusal: the assistant said it could not answer (status no_answer) and the documents truly do not answer the question

Also say whether at least one source actually supports the answer (citation_ok).

Reply with only JSON: {{"label": "correct|partial|incorrect|correct_refusal", "citation_ok": true|false, "reason": "one short sentence"}}"""


def judge(question, verified, system, status, sources):
    """Ask the AI judge (Luna). Returns (label, citation_ok, reason). Never raises on bad JSON."""
    from haic import ask  # imported here so --no-judge needs no key

    prompt = JUDGE_PROMPT.format(
        question=question, verified=verified, system=system, status=status, sources=sources
    )
    try:
        text = ask(prompt, model="luna", max_tokens=500)
        # Take the outermost {...} in case the model adds extra text.
        data = json.loads(text[text.index("{"): text.rindex("}") + 1])
        label = data.get("label")
        if label not in LABELS:
            raise ValueError("bad label")
        return label, bool(data.get("citation_ok")), str(data.get("reason", ""))
    except Exception as exc:  # bad JSON, bad label, or an AI error
        return "needs_review", False, f"Judge output could not be used ({type(exc).__name__})"


def format_check(resp):
    """Turn a CheckResponse into plain text for the judge and the results file."""
    done = "; ".join(f"{s.requirement}: {', '.join(s.courses)}" for s in resp.satisfied)
    todo = "; ".join(f"{r.requirement}: {r.description}" for r in resp.remaining)
    return f"Satisfied: {done}\nRemaining: {todo}\nNotes: {resp.notes or ''}"


def run_row(row):
    """Run one question through its service. Returns (system_answer, status, sources_text)."""
    try:
        if row["feature"] == "ask":
            resp = ask_service.answer(row["question"])
            text = resp.answer
        else:
            courses = [c.strip() for c in row.get("completed_courses", "").split(";") if c.strip()]
            resp = check_service.check(row.get("program", ""), courses)
            text = format_check(resp)
        sources = " | ".join(f"{s.title} ({s.url})" for s in resp.sources)
        return text, resp.status, sources
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}", "error", ""


def accuracy(labels):
    """(correct + correct_refusal) / total, as in docs/EVALUATION.md."""
    if not labels:
        return 0.0
    good = sum(1 for l in labels if l in ("correct", "correct_refusal"))
    return good / len(labels)


def main(argv=None):
    p = argparse.ArgumentParser(description="Run the Navigator evaluation.")
    p.add_argument("--split", choices=["dev", "test", "all"], default="dev")
    p.add_argument("--label", required=True, help="name for this run, used in the file name")
    p.add_argument("--feature", choices=["ask", "check", "all"], default="all")
    p.add_argument("--questions", default=str(ROOT / "eval" / "questions.csv"))
    p.add_argument("--no-judge", action="store_true", help="skip the AI judge")
    p.add_argument("--results-dir", default=str(ROOT / "eval" / "results"))
    args = p.parse_args(argv)

    with open(args.questions, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    selected = [
        r for r in rows
        if not r["id"].startswith("EXAMPLE")
        and (args.split == "all" or r["split"] == args.split)
        and (args.feature == "all" or r["feature"] == args.feature)
    ]

    results = []
    for row in selected:
        system, status, sources = run_row(row)
        if status == "placeholder":
            # Nothing real to grade, so skip the judge (saves AI budget).
            # "no_answer" rows are still judged: they can be correct refusals.
            label, citation_ok, reason = "incorrect", False, "placeholder answer"
        elif args.no_judge:
            label, citation_ok, reason = "not_judged", "", ""
        else:
            label, citation_ok, reason = judge(
                row["question"], row["verified_answer"], system, status, sources
            )
        results.append({
            "id": row["id"], "feature": row["feature"], "category": row["category"],
            "question": row["question"], "verified_answer": row["verified_answer"],
            "system_answer": system, "status": status, "sources": sources,
            "label": label, "citation_ok": citation_ok, "reason": reason,
        })

    out_dir = Path(args.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date.today().isoformat()}_{args.label}.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        w.writeheader()
        w.writerows(results)

    print(f"Questions run: {len(results)} (split={args.split}, feature={args.feature})")
    for feature in ("ask", "check"):
        labels = [r["label"] for r in results if r["feature"] == feature]
        if labels:
            print(f"  {feature}: {accuracy(labels):.0%} ({len(labels)} questions)")
    print(f"  overall: {accuracy([r['label'] for r in results]):.0%}")
    if args.no_judge:
        print("  (judge skipped, so accuracy shows 0%)")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
