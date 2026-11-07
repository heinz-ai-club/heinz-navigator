"""The eval runner should finish with placeholder services and a mocked judge."""

import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_runner():
    spec = importlib.util.spec_from_file_location("run_eval", ROOT / "eval" / "run_eval.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HEADER = (
    "id,feature,category,question,program,completed_courses,verified_answer,"
    "source_url,split,verified_by,date_verified\n"
)


def test_runner_completes_and_skips_examples(tmp_path, monkeypatch, capsys):
    q = tmp_path / "q.csv"
    q.write_text(
        HEADER
        + "EXAMPLE1,ask,policies,Example,,,x,u,dev,AB/CD,2026-11-15\n"
        + "Q001,ask,policies,Can I take pass/fail?,,,Yes,u,dev,AB/CD,2026-11-15\n"
        + "Q002,check,requirements,Case,MS-AIM,95-888;94-806,Need stats,u,dev,AB/CD,2026-11-15\n"
    )
    run_eval = load_runner()
    def judge_must_not_run(*a, **k):
        raise AssertionError("the judge must not be called for placeholder rows")

    monkeypatch.setattr(run_eval, "judge", judge_must_not_run)
    results = tmp_path / "results"

    code = run_eval.main(
        ["--label", "test", "--questions", str(q), "--results-dir", str(results)]
    )
    assert code == 0
    assert "overall: 0%" in capsys.readouterr().out

    files = list(results.glob("*_test.csv"))
    assert len(files) == 1
    rows = list(csv.DictReader(files[0].open(encoding="utf-8")))
    assert [r["id"] for r in rows] == ["Q001", "Q002"]  # example row skipped
    assert all(r["status"] == "placeholder" for r in rows)
    assert all(r["label"] == "incorrect" and r["reason"] == "placeholder answer" for r in rows)


def test_no_answer_rows_are_still_judged(tmp_path, monkeypatch, capsys):
    from app.schemas import AskResponse

    q = tmp_path / "q.csv"
    q.write_text(
        HEADER + "Q001,ask,policies,Unanswerable?,,,Not in documents,u,dev,AB/CD,2026-11-15\n"
    )
    run_eval = load_runner()
    monkeypatch.setattr(
        run_eval.ask_service, "answer",
        lambda question: AskResponse(answer="Please contact the registrar.", sources=[], status="no_answer"),
    )
    calls = []

    def fake_judge(*args, **kwargs):
        calls.append(args)
        return "correct_refusal", False, "documents do not answer it"

    monkeypatch.setattr(run_eval, "judge", fake_judge)
    run_eval.main(["--label", "refusal", "--questions", str(q), "--results-dir", str(tmp_path / "r")])
    assert len(calls) == 1
    assert "overall: 100%" in capsys.readouterr().out
