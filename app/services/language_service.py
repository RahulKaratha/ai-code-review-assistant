from pathlib import Path


LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust"
}


def detect_language(
    repository_path: Path
) -> str:

    extensions = {}

    for file in repository_path.rglob("*"):

        if not file.is_file():
            continue

        extension = file.suffix.lower()

        if not extension:
            continue

        extensions[extension] = (
            extensions.get(extension, 0) + 1
        )

    if not extensions:
        return "unknown"

    dominant_extension = max(
        extensions,
        key=extensions.get
    )

    return LANGUAGE_MAP.get(
        dominant_extension,
        "unknown"
    )