from app.models.schema import ReviewRequest


def build_review_prompt(request: ReviewRequest) -> str:

    metrics = request.metrics

    if request.review_mode == "full":
        code_context = request.codebase or "No source code provided."
        analysis_type = "Perform a full repository code review."
    else:
        code_context = request.code_diff or "No code diff provided."
        analysis_type = "Review only the changes introduced by this commit."

    prompt = f"""
You are a senior software engineer performing a professional code review.

Your task is to identify meaningful engineering issues that traditional
static analysis tools may not fully understand.

Review mode:
{request.review_mode}

Repository:
{request.repository}

Branch:
{request.branch}

Commit:
{request.commit_hash}

Commit message:
{request.commit_message}

Pipeline metrics:
- Cyclomatic complexity: {metrics.complexity}
- Lint issues: {metrics.lint_issues}
- Test coverage: {metrics.test_coverage}%
- Tests passed: {metrics.tests_passed}
- Tests failed: {metrics.tests_failed}

{analysis_type}

Code context:
--------------------
{code_context}
--------------------

Focus on:

1. Logical bugs
2. Security vulnerabilities
3. Performance problems
4. Poor architectural decisions
5. Error-handling problems
6. Maintainability problems
7. Potential edge cases

IMPORTANT:
- Do not simply repeat lint errors or formatting violations.
- Focus on semantic issues that require understanding the code.
- Only report issues that are reasonably supported by the provided code.
- Do not invent vulnerabilities.
- Explain why each issue matters.
- Provide a practical recommendation for fixing each issue.

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
Do not wrap the JSON in ```json code fences.
"""

    return prompt.strip()