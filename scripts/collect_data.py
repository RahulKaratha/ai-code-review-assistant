import subprocess
from pathlib import Path

from app.services.language_service import detect_language


def run_git_command(repository_path: Path, command: list[str]) -> str:

    result = subprocess.run(
        ["git", "-C", str(repository_path), *command],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def get_repository(repository_path: Path) -> str:

    result = subprocess.run(
        ["git", "-C", str(repository_path), "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    return repository_path.name


def get_branch(repository_path: Path) -> str:

    return run_git_command(repository_path, ["branch", "--show-current"])


def get_commit_hash(repository_path: Path) -> str:

    return run_git_command(repository_path, ["rev-parse", "HEAD"])


def get_commit_message(repository_path: Path) -> str:

    return run_git_command(repository_path, ["log", "-1", "--pretty=%B"])


def get_commit_count(repository_path: Path) -> int:

    return int(run_git_command(repository_path, ["rev-list", "--count", "HEAD"]))


def get_code_diff(repository_path: Path) -> str:

    commit_count = get_commit_count(repository_path)

    if commit_count <= 1:
        return run_git_command(
            repository_path, ["show", "--format=", "--no-ext-diff", "HEAD"]
        )

    return run_git_command(repository_path, ["diff", "HEAD~1", "HEAD"])


def get_codebase(repository_path: Path) -> str:

    files = run_git_command(repository_path, ["ls-files", "*.py"])

    if not files:
        return ""

    codebase = []

    for file_path in files.splitlines():
        path = repository_path / file_path

        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8")

            codebase.append(
                f"""
===== {file_path} =====

{content}
"""
            )

        except UnicodeDecodeError:
            continue

    return "\n".join(codebase)


def collect_git_data(repository_path: Path) -> dict:

    commit_count = get_commit_count(repository_path)

    if commit_count <= 1:
        review_mode = "full"

        codebase = get_codebase(repository_path)

        code_diff = None

    else:
        review_mode = "diff"

        codebase = None

        code_diff = get_code_diff(repository_path)

    return {
        "repository": get_repository(repository_path),
        "language": detect_language(repository_path),
        "branch": get_branch(repository_path),
        "commit_hash": get_commit_hash(repository_path),
        "commit_message": get_commit_message(repository_path),
        "review_mode": review_mode,
        "code_diff": code_diff,
        "codebase": codebase,
    }


if __name__ == "__main__":
    data = collect_git_data(Path.cwd())

    print(data)
