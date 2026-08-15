from app.models.schema import ReviewRequest


def build_review_prompt(request: ReviewRequest) -> str:

    metrics = request.metrics

    metrics_section = []

    if metrics.complexity is not None:
        metrics_section.append(f"- Cyclomatic complexity: {metrics.complexity}")

    if metrics.lint_issues is not None:
        metrics_section.append(f"- Lint issues: {metrics.lint_issues}")

    if metrics.security_issues is not None:
        metrics_section.append(f"- Security issues: {metrics.security_issues}")

    if metrics.test_coverage is not None:
        metrics_section.append(f"- Test coverage: {metrics.test_coverage}%")

    if metrics.tests_passed is not None:
        metrics_section.append(f"- Tests passed: {metrics.tests_passed}")

    if metrics.tests_failed is not None:
        metrics_section.append(f"- Tests failed: {metrics.tests_failed}")

    if metrics.risk_score is not None:
        metrics_section.append(f"- Calculated risk score: {metrics.risk_score}")

    metrics_text = "\n".join(metrics_section)

    if not metrics_text:
        metrics_text = "No pipeline metrics are available for this repository."

    if request.review_mode == "full":
        code_context = request.codebase or "No source code provided."

        analysis_type = """
    Perform a full repository code review.

    Focus on:

    1. Architecture
    2. Code organization
    3. Dependency management
    4. Test quality
    5. CI/CD configuration
    6. Security
    7. Scalability
    """

    elif request.review_mode == "branch":
        code_context = request.code_diff or "No code diff provided."

        analysis_type = """
    Review the changes between the base branch and target branch.

    Focus on:

    1. Pull request quality
    2. Architectural impact
    3. Security vulnerabilities
    4. Regression risks
    5. Test coverage
    6. Breaking changes
    """

    else:
        code_context = request.code_diff or "No code diff provided."

        analysis_type = """
    Review only the latest commit.

    Focus on:

    1. Logical bugs
    2. Security vulnerabilities
    3. Performance problems
    4. Poor architectural decisions
    5. Error-handling problems
    6. Maintainability problems
    7. Potential edge cases
    """

    prompt = f"""
You are a senior software engineer performing a professional code review.

Your task is to identify meaningful engineering issues that traditional
static analysis tools may not fully understand.

Review mode:
{request.review_mode}

Repository:
{request.repository}

Repository language:
{request.language}

Branch:
{request.branch}

Commit:
{request.commit_hash}

Commit message:
{request.commit_message}

Pipeline metrics:

{metrics_text}

{analysis_type}

Code context:
--------------------
{code_context}
--------------------
IMPORTANT:

- Use the pipeline metrics only as supporting evidence.
- Some metrics may be unavailable depending on the repository language.
- If a metric is unavailable, do not assume that its value is zero.
- Do not assume that the repository is written in Python.
- Apply language-specific engineering best practices.
- Treat the calculated risk score as an indicator, not as the final decision.
- Do not simply repeat lint errors, test failures, complexity scores, or security scan findings.
- Focus on semantic issues that require understanding the code.
- Correlate code changes with the available metrics whenever possible.
- Only report issues that are reasonably supported by the provided code.
- Do not invent vulnerabilities.
- Explain why each issue matters.
- Provide practical recommendations for fixing each issue.
- When reviewing a branch or pull request, pay special attention to regression risks and breaking changes.
- When reviewing an entire repository, pay special attention to architecture, code organization, CI/CD configuration, dependency management, and scalability.

Risk score interpretation:

0-2 = LOW
2-5 = MEDIUM
5-8 = HIGH
8+ = CRITICAL

Return ONLY valid JSON using exactly this structure:
{{
    "overall_risk": "LOW",
    "summary": "Brief overall assessment of the code.",
    "issues": [
        {{
            "category": "Security",
            "severity": "High",
            "description": "Description of the issue.",
            "recommendation": "Recommended fix."
        }}
    ],
    "positive_observations": [
        "Something the code does well."
    ]
}}

Allowed values for overall_risk:

- LOW
- MEDIUM
- HIGH
- CRITICAL

Allowed severity values:

- Low
- Medium
- High
- Critical

If no meaningful issues are found, return an empty issues array.

Do not include Markdown.
Do not wrap the JSON in ```json code fences."""

    return prompt.strip()
