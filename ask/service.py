# GROUP 1: replace the body of answer() with the real Ask Heinz logic.
# Keep the function name and the return type. The format is fixed in docs/API_CONTRACT.md.

from app.schemas import AskResponse, Source


def answer(question: str) -> AskResponse:
    """Placeholder: says the feature is not built yet."""
    return AskResponse(
        answer=f"Ask Heinz is not built yet. You asked: {question}",
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
