import subprocess


def run_git_command(command: list[str]) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.strip()


def get_repository() -> str:
    return run_git_command(
        ["git", "config", "--get", "remote.origin.url"]
    )


def get_branch() -> str:
    return run_git_command(
        ["git", "branch", "--show-current"]
    )


def get_commit_hash() -> str:
    return run_git_command(
        ["git", "rev-parse", "HEAD"]
    )


def get_commit_message() -> str:
    return run_git_command(
        ["git", "log", "-1", "--pretty=%B"]
    )


def get_commit_count() -> int:
    output = run_git_command(
        ["git", "rev-list", "--count", "HEAD"]
    )

    return int(output)


def get_code_diff() -> str:

    commit_count = get_commit_count()

    if commit_count <= 1:
        return run_git_command(
            ["git", "show", "--format=", "--no-ext-diff", "HEAD"]
        )

    return run_git_command(
        ["git", "diff", "HEAD~1", "HEAD"]
    )


def collect_git_data() -> dict:

    commit_count = get_commit_count()

    if commit_count <= 1:
        review_mode = "full"
        code_diff = None
        codebase = get_codebase()

    else:
        review_mode = "diff"
        code_diff = get_code_diff()
        codebase = None

    return {
        "repository": get_repository(),
        "branch": get_branch(),
        "commit_hash": get_commit_hash(),
        "commit_message": get_commit_message(),
        "review_mode": review_mode,
        "code_diff": code_diff,
        "codebase": codebase,
        "commit_count": commit_count
    }


def get_codebase() -> str:

    return run_git_command(
        [
            "git",
            "ls-files",
            "*.py"
        ]
    )


if __name__ == "__main__":
    data = collect_git_data()

    print(data)