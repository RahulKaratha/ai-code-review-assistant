from typing import Literal, Optional

from pydantic import BaseModel, Field


class PipelineMetrics(BaseModel):
    complexity: Optional[float] = None
    lint_issues: int = 0
    test_coverage: Optional[float] = None
    tests_passed: Optional[int] = None
    tests_failed: Optional[int] = None


class ReviewRequest(BaseModel):
    repository: str
    branch: str
    commit_hash: str
    commit_message: str

    review_mode: Literal["full", "diff"] = Field(
        default="diff",
        description="Review mode."
    )

    code_diff: Optional[str] = None
    codebase: Optional[str] = None

    metrics: PipelineMetrics


class ReviewIssue(BaseModel):
    category: str
    severity: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]
    description: str
    recommendation: str


class ReviewResponse(BaseModel):
    overall_risk: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]

    summary: str

    issues: list[ReviewIssue]

    positive_observations: list[str]