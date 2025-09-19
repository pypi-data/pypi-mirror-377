"""Git operations and utilities."""

from __future__ import annotations
import subprocess as sp
from .error import KnownError

# Default files to exclude from git diff
FILES_TO_EXCLUDE = [
    # Python build artifacts
    "*.pyc",
    "__pycache__/**",
    "*.pyo",
    "*.pyd",
    ".Python",
    "build/**",
    "develop-eggs/**",
    "dist/**",
    "downloads/**",
    "eggs/**",
    ".eggs/**",
    "lib/**",
    "lib64/**",
    "parts/**",
    "sdist/**",
    "var/**",
    "wheels/**",
    "*.egg-info/**",
    ".installed.cfg",
    "*.egg",
    "MANIFEST",
    
    # Virtual environments
    ".venv/**",
    "venv/**",
    ".env/**",
    "env/**",
    ".virtualenv/**",
    "virtualenv/**",
    
    # Testing and coverage
    ".pytest_cache/**",
    ".coverage",
    "coverage.xml",
    "*.cover",
    ".hypothesis/**",
    ".tox/**",
    "htmlcov/**",
    
    # IDE and editor files
    ".vscode/**",
    ".idea/**",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    
    # Jupyter Notebook
    ".ipynb_checkpoints/**",
    
    # mypy
    ".mypy_cache/**",
    ".dmypy.json",
    "dmypy.json",
    
    # Logs and temporary files
    "*.log",
    "*.tmp",
    "*.temp",
    "*.cache",
    
    # Package manager files
    "Pipfile.lock",
    "poetry.lock",
    "requirements*.txt",
    
    # Documentation builds
    "docs/_build/**",
    "site/**",
]


def exclude_from_diff(path: str) -> str:
    """Format path as git exclude pattern."""
    return f":(exclude){path}"


def assert_repo() -> str:
    """Ensure we're in a git repository and return repo root."""
    try:
        result = sp.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            raise KnownError("The current directory must be a Git repository!")
        
        return result.stdout.strip()
    except FileNotFoundError:
        raise KnownError("Git is not installed or not found in PATH")


def get_staged_diff(exclude_files: list[str] | None = None) -> dict | None:
    """Get staged changes diff with file exclusions."""
    diff_cached = ["diff", "--cached", "--diff-algorithm=minimal"]
    exclude_patterns = [
        *map(exclude_from_diff, FILES_TO_EXCLUDE),
        *map(exclude_from_diff, exclude_files or [])
    ]
    
    try:
        # Get list of staged files
        files_result = sp.run(
            ["git", *diff_cached, "--name-only", *exclude_patterns],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = files_result.stdout.strip()
        if not files:
            return None
        
        # Get the actual diff
        diff_result = sp.run(
            ["git", *diff_cached, *exclude_patterns],
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "files": files.split("\n"),
            "diff": diff_result.stdout,
        }
    except sp.CalledProcessError as e:
        raise KnownError(f"Git error: {e.stderr or e.stdout}")


def get_detected_message(files: list[str]) -> str:
    """Generate a message describing detected staged files."""
    count = len(files)
    plural = "s" if count > 1 else ""
    return f"Detected {count:,} staged file{plural}"


def estimate_token_count(text: str) -> int:
    """Rough estimation: 1 token ≈ 4 characters for English text."""
    return max(1, len(text) // 4)


def chunk_diff(diff: str, max_tokens: int = 4000) -> list[str]:
    """Split diff into chunks that fit within token limits."""
    estimated_tokens = estimate_token_count(diff)
    
    if estimated_tokens <= max_tokens:
        return [diff]
    
    chunks = []
    lines = diff.split("\n")
    current_chunk = ""
    current_tokens = 0
    
    for line in lines:
        line_tokens = estimate_token_count(line)
        
        # If adding this line would exceed the limit, start a new chunk
        if current_tokens + line_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
            current_tokens = line_tokens
        else:
            current_chunk += line + "\n"
            current_tokens += line_tokens
    
    # Add the last chunk if it has content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def get_diff_summary(exclude_files: list[str] | None = None) -> dict | None:
    """Get a summary of changes for very large diffs."""
    diff_cached = ["diff", "--cached", "--diff-algorithm=minimal"]
    exclude_patterns = [
        *map(exclude_from_diff, FILES_TO_EXCLUDE),
        *map(exclude_from_diff, exclude_files or [])
    ]
    
    try:
        # Get list of staged files
        files_result = sp.run(
            ["git", *diff_cached, "--name-only", *exclude_patterns],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = files_result.stdout.strip()
        if not files:
            return None
        
        file_list = [f for f in files.split("\n") if f]
        
        # Get stats for each file
        file_stats = []
        for file in file_list:
            try:
                stat_result = sp.run(
                    ["git", *diff_cached, "--numstat", "--", file],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                parts = stat_result.stdout.strip().split("\t")
                if len(parts) >= 2:
                    try:
                        additions = int(parts[0]) if parts[0] != "-" else 0
                        deletions = int(parts[1]) if parts[1] != "-" else 0
                    except ValueError:
                        additions = deletions = 0
                else:
                    additions = deletions = 0
                
                file_stats.append({
                    "file": file,
                    "additions": additions,
                    "deletions": deletions,
                    "changes": additions + deletions
                })
            except sp.CalledProcessError:
                file_stats.append({
                    "file": file,
                    "additions": 0,
                    "deletions": 0,
                    "changes": 0
                })
        
        return {
            "files": file_list,
            "file_stats": file_stats,
            "total_changes": sum(stat["changes"] for stat in file_stats)
        }
    except sp.CalledProcessError as e:
        raise KnownError(f"Git error: {e.stderr or e.stdout}")


def split_diff_by_file(diff: str) -> list[str]:
    """Split diff into per-file chunks."""
    parts = []
    current = ""
    lines = diff.split("\n")
    
    for line in lines:
        if line.startswith("diff --git "):
            if current.strip():
                parts.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    
    if current.strip():
        parts.append(current.strip())
    
    return parts


def build_compact_summary(exclude_files: list[str] | None = None, max_files: int = 20) -> str | None:
    """Build a compact summary of changes for large diffs."""
    summary = get_diff_summary(exclude_files)
    if not summary:
        return None
    
    file_stats = summary["file_stats"]
    sorted_stats = sorted(file_stats, key=lambda x: x["changes"], reverse=True)
    top_files = sorted_stats[:max(1, max_files)]
    
    total_files = len(summary["files"])
    total_changes = summary["total_changes"]
    total_additions = sum(f["additions"] for f in file_stats)
    total_deletions = sum(f["deletions"] for f in file_stats)
    
    lines = [
        f"Files changed: {total_files}",
        f"Additions: {total_additions}, Deletions: {total_deletions}, Total changes: {total_changes}",
        "Top files by changes:"
    ]
    
    for f in top_files:
        lines.append(f"- {f['file']} (+{f['additions']} / -{f['deletions']}, {f['changes']} changes)")
    
    if len(sorted_stats) > len(top_files):
        lines.append(f"…and {len(sorted_stats) - len(top_files)} more files")
    
    return "\n".join(lines)


# Legacy function aliases for backward compatibility
estimate_tokens = estimate_token_count