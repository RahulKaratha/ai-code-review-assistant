from fastapi import APIRouter, HTTPException

from app.models.schema import ReviewRequest, ReviewResponse
from app.services.analyzer import CodeAnalyzer


router = APIRouter()

analyzer = CodeAnalyzer()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-code-review-assistant"
    }


@router.post(
    "/analyze",
    response_model=ReviewResponse
)
def analyze_code(request: ReviewRequest):

    try:
        return analyzer.analyze(request)

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )