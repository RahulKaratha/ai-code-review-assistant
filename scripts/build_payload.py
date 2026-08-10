import json

from scripts.collect_data import collect_git_data
from app.services.metrics_service import collect_metrics


def build_payload() -> dict:

    git_data = collect_git_data()

    metrics = collect_metrics()

    payload = {
        "repository": git_data["repository"],
        "branch": git_data["branch"],
        "commit_hash": git_data["commit_hash"],
        "commit_message": git_data["commit_message"],
        "review_mode": git_data["review_mode"],
        "code_diff": git_data["code_diff"],
        "codebase": git_data["codebase"],
        "metrics": metrics
    }

    return payload


if __name__ == "__main__":

    payload = build_payload()

    print(
        json.dumps(
            payload,
            indent=4
        )
    )