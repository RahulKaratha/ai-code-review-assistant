import subprocess
import re
from pathlib import Path


def run_command(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        capture_output=True,
        text=True
    )


def get_lint_issues() -> int:
    result = run_command(
        ["ruff", "check", ".", "--output-format", "concise"]
    )

    if not result.stdout.strip():
        return 0

    return len(result.stdout.strip().splitlines())


def get_complexity() -> float | None:
    result = run_command(
        ["radon", "cc", ".", "-a", "-s"]
    )

    if result.returncode not in (0, 1):
        return None

    match = re.search(
        r"Average complexity:\s*([A-Z])\s*\(([\d.]+)\)",
        result.stdout
    )

    if not match:
        return None

    return float(match.group(2))


def get_test_results() -> tuple[int, int]:
    result = run_command(
        [
            "pytest",
            "--tb=no",
            "-q"
        ]
    )

    output = result.stdout + result.stderr

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

    return passed, failed


def get_test_coverage() -> float | None:
    result = run_command(
        [
            "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "-q"
        ]
    )

    output = result.stdout + result.stderr

    match = re.search(
        r"TOTAL\s+\d+\s+\d+\s+\d+\s+(\d+)%",
        output
    )

    if not match:
        return None

    return float(match.group(1))


def collect_metrics() -> dict:

    lint_issues = get_lint_issues()

    complexity = get_complexity()

    tests_passed, tests_failed = get_test_results()

    coverage = get_test_coverage()

    return {
        "complexity": complexity,
        "lint_issues": lint_issues,
        "test_coverage": coverage,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed
    }


if __name__ == "__main__":

    metrics = collect_metrics()

    print("\n===== PIPELINE METRICS =====\n")

    for key, value in metrics.items():
        print(f"{key}: {value}")