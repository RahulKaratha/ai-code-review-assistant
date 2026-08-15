from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PipelineMetrics(BaseModel):
    
    complexity: float

    lint_issues: int

    security_issues: int

    test_coverage: float

    tests_passed: int

    tests_failed: int

    risk_score: float

class ReviewRequest(BaseModel):
    repository: str
    language: str
    branch: str
    commit_hash: str
    commit_message: str
    

    review_mode: Literal["full", "diff","latest","branch"] = Field(
        default="latest",
        description="Review mode."
    )

    code_diff: str | None = None
    codebase: str | None = None

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

class RepositoryReviewRequest(BaseModel):

    repository_url: str

    review_mode: Literal["latest", "full", "branch"] = "latest"

    branch: str = "main"

    base_branch: str | None = None

    target_branch: str | None = None

    @field_validator("repository_url")
    @classmethod
    def validate_repository_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("repository_url must not be empty.")
        if not v.startswith(("http://", "https://", "git@")):
            raise ValueError("repository_url must be a valid HTTP, HTTPS, or SSH git URL.")
        return v

    @field_validator("base_branch", "target_branch", mode="before")
    @classmethod
    def validate_branch_names(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Branch name must not be blank.")
        return v

    def validate_branch_review(self) -> None:
        if self.review_mode == "branch" and (not self.base_branch or not self.target_branch):
            raise ValueError("base_branch and target_branch are required for branch review mode.")