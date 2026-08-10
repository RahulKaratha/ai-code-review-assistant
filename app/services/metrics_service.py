import re
import subprocess


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
        r"Average complexity:\s*[A-Z]\s*\(([\d.]+)\)",
        result.stdout
    )

    if not match:
        return None

    return float(match.group(1))


def get_test_metrics() -> tuple[int, int, float | None]:

    result = run_command(
        [
            "python",
            "-m",
            "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--tb=no",
            "-q"
        ]
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


def collect_metrics() -> dict:

    lint_issues = get_lint_issues()

    complexity = get_complexity()

    tests_passed, tests_failed, coverage = (
        get_test_metrics()
    )

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