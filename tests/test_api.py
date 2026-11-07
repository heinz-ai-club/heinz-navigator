"""Contract tests for the shell. No test calls a real AI model."""

from fastapi.testclient import TestClient

from app.main import app
import pytest
from pydantic import ValidationError

from app.schemas import AskResponse, CheckResponse

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ask_valid():
    r = client.post("/api/ask", json={"question": "Can I take a course pass/fail?"})
    assert r.status_code == 200
    body = AskResponse.model_validate(r.json())
    assert body.status == "placeholder"
    assert body.model is None
    assert len(body.sources) >= 1


def test_ask_empty_is_422():
    assert client.post("/api/ask", json={"question": ""}).status_code == 422


def test_ask_too_long_is_422():
    assert client.post("/api/ask", json={"question": "x" * 1001}).status_code == 422


def test_check_valid():
    r = client.post(
        "/api/check",
        json={"program": "MS-AIM", "completed_courses": ["95-888", "94-806"], "notes": None},
    )
    assert r.status_code == 200
    body = CheckResponse.model_validate(r.json())
    assert body.program == "MS-AIM"
    assert body.satisfied[0].courses == ["95-888", "94-806"]


def test_check_too_many_courses_is_422():
    courses = [f"95-{i:03d}" for i in range(61)]
    r = client.post("/api/check", json={"program": "MS-AIM", "completed_courses": courses})
    assert r.status_code == 422


def test_index_is_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_service_error_returns_generic_500(monkeypatch):
    def boom(question):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr("ask.service.answer", boom)
    r = client.post("/api/ask", json={"question": "hi"})
    assert r.status_code == 500
    assert r.json() == {"detail": "Something went wrong. Please try again."}


# ---- "ok" responses must cite at least one source (docs/API_CONTRACT.md) ----

def test_ask_ok_without_sources_is_rejected():
    with pytest.raises(ValidationError, match="API_CONTRACT.md"):
        AskResponse(answer="Yes.", sources=[], status="ok")


def test_check_ok_without_sources_is_rejected():
    with pytest.raises(ValidationError, match="API_CONTRACT.md"):
        CheckResponse(program="MS-AIM", satisfied=[], remaining=[], sources=[], status="ok")


@pytest.mark.parametrize("status", ["no_answer", "placeholder"])
def test_ask_other_statuses_are_valid_without_sources(status):
    assert AskResponse(answer="x", sources=[], status=status).status == status


@pytest.mark.parametrize("status", ["unknown_program", "placeholder"])
def test_check_other_statuses_are_valid_without_sources(status):
    r = CheckResponse(program="X", satisfied=[], remaining=[], sources=[], status=status)
    assert r.status == status


def test_ok_without_sources_from_a_service_gives_generic_500(monkeypatch):
    def bad_service(question):
        return AskResponse(answer="Yes.", sources=[], status="ok")

    monkeypatch.setattr("ask.service.answer", bad_service)
    r = client.post("/api/ask", json={"question": "hi"})
    assert r.status_code == 500
    assert r.json() == {"detail": "Something went wrong. Please try again."}
