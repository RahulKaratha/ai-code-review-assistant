from app.models.schema import PipelineMetrics, ReviewRequest
from app.services.analyzer import CodeAnalyzer


def test_analyzer_returns_structured_review(monkeypatch):

    request = ReviewRequest(
        repository="test-repository",
        language="python",
        branch="main",
        commit_hash="abc123",
        commit_message="Test commit",
        review_mode="diff",
        code_diff="def add(a, b): return a + b",
        metrics=PipelineMetrics(
            complexity=1.0,
            lint_issues=0,
            security_issues=0,
            test_coverage=100.0,
            tests_passed=1,
            tests_failed=0,
            risk_score=0.1,
        ),
    )

    expected_review = {
        "overall_risk": "LOW",
        "summary": "No significant issues found.",
        "issues": [],
        "positive_observations": ["Simple function with low complexity."],
    }

    class FakeLLMService:
        def generate_review(self, prompt):
            return expected_review

    analyzer = CodeAnalyzer()

    analyzer.llm_service = FakeLLMService()

    result = analyzer.analyze(request)

    assert result.overall_risk == "LOW"
    assert result.summary == "No significant issues found."
    assert len(result.issues) == 0
    assert len(result.positive_observations) == 1
