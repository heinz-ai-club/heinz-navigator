"""
Pydantic models that match docs/API_CONTRACT.md exactly.
Do not change field names or rules without agreement (see the contract).
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class Source(BaseModel):
    title: str                       # name of the document and section
    url: str                         # public link to the page or PDF
    snippet: Optional[str] = None    # the exact passage the answer relies on


# ---- Feature 1: Ask Heinz -------------------------------------------------

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


def _require_source_when_ok(status: str, sources: list) -> None:
    """Shared rule from docs/API_CONTRACT.md: an "ok" response must cite a source."""
    if status == "ok" and len(sources) < 1:
        raise ValueError(
            'A response with status "ok" must include at least one source. '
            "Return status \"no_answer\" (or \"unknown_program\" for the checker) "
            "if you cannot cite one. See docs/API_CONTRACT.md."
        )


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]            # at least one when status is "ok"
    status: Literal["ok", "no_answer", "placeholder"]
    model: Optional[str] = None

    @model_validator(mode="after")
    def check_sources(self):
        _require_source_when_ok(self.status, self.sources)
        return self


# ---- Feature 2: Requirement Checker ---------------------------------------

class CheckRequest(BaseModel):
    program: str
    completed_courses: list[str] = Field(max_length=60)
    notes: Optional[str] = Field(default=None, max_length=500)


class SatisfiedRequirement(BaseModel):
    requirement: str
    courses: list[str]


class Requirement(BaseModel):
    requirement: str
    description: str
    options: list[str] = []          # may be empty


class CheckResponse(BaseModel):
    program: str
    satisfied: list[SatisfiedRequirement]
    remaining: list[Requirement]
    notes: Optional[str] = None
    sources: list[Source]            # at least one when status is "ok"
    status: Literal["ok", "unknown_program", "placeholder"]
    model: Optional[str] = None

    @model_validator(mode="after")
    def check_sources(self):
        _require_source_when_ok(self.status, self.sources)
        return self
