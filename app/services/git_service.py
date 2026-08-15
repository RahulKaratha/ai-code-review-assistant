import shutil
import subprocess
import tempfile
from pathlib import Path


class GitService:
    def __init__(self):
        self.temp_root = Path(tempfile.mkdtemp(prefix="ai-code-review-"))

    def clone_repository(self, repository_url: str, branch: str | None = None) -> Path:

        repository_path = self.temp_root / "repository"

        command = [
            "git",
            "clone",
        ]

        if branch:
            command.extend(
                [
                    "--branch",
                    branch,
                ]
            )

        command.extend(
            [
                "--depth",
                "50",
                repository_url,
                str(repository_path),
            ]
        )

        try:
            subprocess.run(command, capture_output=True, text=True, check=True)  # nosec B603 B607

        except FileNotFoundError as exc:
            raise RuntimeError("Git is not installed or could not be found.") from exc

        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"Failed to clone repository: {exc.stderr.strip()}"
            ) from exc

        return repository_path

    def get_branch(self, repository_path: Path) -> str:

        result = subprocess.run(  # nosec B603 B607
            ["git", "-C", str(repository_path), "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    def get_commit_hash(self, repository_path: Path) -> str:

        result = subprocess.run(  # nosec B603 B607
            ["git", "-C", str(repository_path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    def get_commit_message(self, repository_path: Path) -> str:

        result = subprocess.run(  # nosec B603 B607
            ["git", "-C", str(repository_path), "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    def cleanup(self) -> None:

        if self.temp_root.exists():
            shutil.rmtree(self.temp_root, ignore_errors=True)

    def fetch_branch(self, repository_path: Path, branch: str):

        subprocess.run(  # nosec B603 B607
            ["git", "-C", str(repository_path), "fetch", "origin", branch],
            check=True,
            capture_output=True,
            text=True,
        )

    def get_branch_diff(
        self, repository_path: Path, base_branch: str, target_branch: str
    ):

        self.fetch_branch(repository_path, base_branch)

        self.fetch_branch(repository_path, target_branch)

        result = subprocess.run(  # nosec B603 B607
            [
                "git",
                "-C",
                str(repository_path),
                "diff",
                f"origin/{base_branch}",
                f"origin/{target_branch}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return result.stdout

    def get_diff_stats(
        self, repository_path: Path, base_branch: str, target_branch: str
    ):

        result = subprocess.run(  # nosec B603 B607
            [
                "git",
                "-C",
                str(repository_path),
                "diff",
                "--shortstat",
                f"origin/{base_branch}",
                f"origin/{target_branch}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        return result.stdout
