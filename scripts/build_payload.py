from pathlib import Path

from app.models.schema import PipelineMetrics, ReviewRequest
from app.services.language_service import detect_language
from app.services.metrics_service import collect_metrics
from scripts.collect_data import collect_git_data


def build_payload(
    repository_path: Path,
    review_mode: str = "latest",
    custom_diff: str | None = None
) -> ReviewRequest:

    git_data = collect_git_data(
        repository_path
    )

    git_data["review_mode"] = review_mode

    if custom_diff:

        git_data["code_diff"] = custom_diff
        git_data["codebase"] = None

    metrics_data = collect_metrics(
        repository_path
    )

    language = detect_language(
        repository_path
    )

    return ReviewRequest(

        repository=git_data["repository"],

        language=language,

        branch=git_data["branch"],

        commit_hash=git_data["commit_hash"],

        commit_message=git_data["commit_message"],

        review_mode=git_data["review_mode"],

        code_diff=git_data["code_diff"],

        codebase=git_data["codebase"],

        metrics=PipelineMetrics(

            complexity=metrics_data["complexity"],

            lint_issues=metrics_data["lint_issues"],

            security_issues=metrics_data["security_issues"],

            test_coverage=metrics_data["test_coverage"],

            tests_passed=metrics_data["tests_passed"],

            tests_failed=metrics_data["tests_failed"],

            risk_score=metrics_data["risk_score"]

        )
    )