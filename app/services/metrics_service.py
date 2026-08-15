import re
import subprocess
from pathlib import Path

from app.services.language_service import detect_language


def run_command(
    command: list[str],
    repository_path: Path
) -> subprocess.CompletedProcess:

    return subprocess.run(
        command,
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=False
    )


def get_lint_issues(
    repository_path: Path
) -> int:

    result = run_command(
        [
            "ruff",
            "check",
            ".",
            "--output-format",
            "concise"
        ],
        repository_path
    )

    if not result.stdout.strip():
        return 0

    return len(
        result.stdout.strip().splitlines()
    )


def get_complexity(
    repository_path: Path
) -> float | None:

    result = run_command(
        [
            "radon",
            "cc",
            ".",
            "-a",
            "-s"
        ],
        repository_path
    )

    if result.returncode not in (0, 1):
        return None

    match = re.search(
        r"Average complexity:\s*[A-Z]\s*\(([\d.]+)\)",
        result.stdout
    )

    if not match:
        return None

    return float(match.group(1))


def get_test_metrics(
    repository_path: Path
) -> tuple[int, int, float | None]:

    result = run_command(
        [
            "python",
            "-m",
            "pytest",
            "--cov=.",
            "--cov-report=term-missing",
            "--tb=no",
            "-q"
        ],
        repository_path
    )

    output = result.stdout + result.stderr

    # -------------------------
    # Test results
    # -------------------------

    passed_match = re.search(
        r"(\d+)\s+passed",
        output
    )

    failed_match = re.search(
        r"(\d+)\s+failed",
        output
    )

    passed = (
        int(passed_match.group(1))
        if passed_match
        else 0
    )

    failed = (
        int(failed_match.group(1))
        if failed_match
        else 0
    )

    # -------------------------
    # Coverage
    # -------------------------

    coverage_match = re.search(
        r"TOTAL\s+\d+\s+\d+\s+(\d+)%",
        output
    )

    coverage = (
        float(coverage_match.group(1))
        if coverage_match
        else None
    )

    return passed, failed, coverage

def get_security_issues(
    repository_path: Path
) -> int:

    result = run_command(
    [
        "bandit",
        "-r",
        ".",
        "-x",
        "tests,__pycache__,.pytest_cache,htmlcov,venv"
    ],
    repository_path
)

    output = (
        result.stdout
        + result.stderr
    )

    low_match = re.search(
        r"Low:\s+(\d+)",
        output
    )

    medium_match = re.search(
        r"Medium:\s+(\d+)",
        output
    )

    high_match = re.search(
        r"High:\s+(\d+)",
        output
    )

    medium = (
        int(medium_match.group(1))
        if medium_match
        else 0
    )

    high = (
        int(high_match.group(1))
        if high_match
        else 0
    )

    return (
       medium
        + high
    )

def calculate_risk_score(
    complexity,
    lint_issues,
    security_issues,
    tests_failed
) -> float:

    complexity = complexity or 0
    lint_issues = lint_issues or 0
    security_issues = security_issues or 0
    tests_failed = tests_failed or 0

    risk_score = (
        complexity * 0.2
        + lint_issues * 0.1
        + security_issues * 0.4
        + tests_failed * 0.3
    )

    return round(risk_score, 2)

def collect_metrics(
    repository_path: Path
) -> dict:

    language = detect_language(
        repository_path
    )

    if language == "python":

        lint_issues = get_lint_issues(
            repository_path
        )

        complexity = get_complexity(
            repository_path
        )

        security_issues = get_security_issues(
            repository_path
        )

        tests_passed, tests_failed, coverage = (
            get_test_metrics(
                repository_path
            )
        )

    else:

        lint_issues = 0

        complexity = 0

        security_issues = 0

        tests_passed = 0

        tests_failed = 0

        coverage = 0

    risk_score = calculate_risk_score(

        complexity,

        lint_issues,

        security_issues,

        tests_failed

    )

    return {

        "complexity": complexity or 0,

        "lint_issues": lint_issues or 0,

        "security_issues": security_issues or 0,

        "test_coverage": coverage or 0,

        "tests_passed": tests_passed or 0,

        "tests_failed": tests_failed or 0,

        "risk_score": risk_score

    }
if __name__ == "__main__":

    # Used only when testing this file directly.
    repository_path = Path.cwd()

    metrics = collect_metrics(
        repository_path
    )

    print("\n===== PIPELINE METRICS =====\n")

    for key, value in metrics.items():
        print(f"{key}: {value}")

