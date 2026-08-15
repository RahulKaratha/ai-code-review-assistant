from fastapi import APIRouter, HTTPException

from app.models.schema import RepositoryReviewRequest, ReviewRequest, ReviewResponse
from app.services.analyzer import CodeAnalyzer
from app.services.git_service import GitService
from scripts.build_payload import build_payload
from scripts.collect_data import collect_git_data

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

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=503,
            detail=f"Analysis service unavailable: {exc}"
        )


@router.post("/review")
def review_repository(
    request: RepositoryReviewRequest
):

    try:
        request.validate_branch_review()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    git_service = GitService()

    try:

        try:
            repository_path = git_service.clone_repository(
                request.repository_url,
                request.branch
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        try:
            if request.review_mode == "branch":

                diff = git_service.get_branch_diff(
                    repository_path,
                    request.base_branch,
                    request.target_branch
                )

                payload = build_payload(
                    repository_path,
                    review_mode="branch",
                    custom_diff=diff
                )

            elif request.review_mode == "full":

                payload = build_payload(
                    repository_path,
                    review_mode="full"
                )

                payload.codebase = collect_git_data(
                    repository_path
                )["codebase"]

                payload.code_diff = None

            else:

                payload = build_payload(
                    repository_path,
                    review_mode="latest"
                )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to prepare repository data: {exc}"
            )

        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error building payload: {exc}"
            )

        try:
            return analyzer.analyze(payload)

        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=503,
                detail=f"Analysis service unavailable: {exc}"
            )

    finally:

        git_service.cleanup()
