# GROUP 2: replace the body of check() with the real Requirement Checker logic.
# Keep the function name and the return type. The format is fixed in docs/API_CONTRACT.md.

from typing import Optional

from app.schemas import CheckResponse, Requirement, SatisfiedRequirement, Source


def check(
    program: str, completed_courses: list[str], notes: Optional[str] = None
) -> CheckResponse:
    """Placeholder: echoes the program and lists the courses as one satisfied item."""
    return CheckResponse(
        program=program,
        satisfied=[
            SatisfiedRequirement(requirement="Placeholder", courses=completed_courses)
        ],
        remaining=[
            Requirement(
                requirement="Example requirement",
                description="The Requirement Checker is not built yet.",
                options=[],
            )
        ],
        notes="This is placeholder output, not a real degree check.",
        sources=[
            Source(
                title="Heinz College (example source)",
                url="https://www.heinz.cmu.edu/",
                snippet=None,
            )
        ],
        status="placeholder",
        model=None,
    )
