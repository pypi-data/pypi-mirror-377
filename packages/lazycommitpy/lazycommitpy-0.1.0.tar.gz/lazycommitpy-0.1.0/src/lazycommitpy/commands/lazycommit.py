"""Main lazycommit command implementation."""

from __future__ import annotations
import subprocess as sp
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from ..utils.git import assert_repo, get_staged_diff, estimate_tokens
from ..utils.config import load
from ..utils.error import KnownError
from ..utils.groq import generate_commit_message_from_chunks, generate_commit_message_from_summary
from ..utils.git import build_compact_summary

console = Console()

ASCII_LOGO = """╔──────────────────────────────────────────────────────────────────────────────────────╗
│                                                                                      │
│ ██╗      █████╗ ███████╗██╗   ██╗ ██████╗ ██████╗ ███╗   ███╗███╗   ███╗██╗████████╗ │
│ ██║     ██╔══██╗╚══███╔╝╚██╗ ██╔╝██╔════╝██╔═══██╗████╗ ████║████╗ ████║██║╚══██╔══╝ │
│ ██║     ███████║  ███╔╝  ╚████╔╝ ██║     ██║   ██║██╔████╔██║██╔████╔██║██║   ██║    │
│ ██║     ██╔══██║ ███╔╝    ╚██╔╝  ██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██║   ██║    │
│ ███████╗██║  ██║███████╗   ██║   ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║   ██║    │
│ ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝   ╚═╝    │
│                                                                                      │
╚──────────────────────────────────────────────────────────────────────────────────────╝"""


def run(generate: int | None, exclude: list[str], stage_all: bool, commit_type: str | None, raw_git_args: list[str]) -> int:
    """Run the main lazycommit command."""
    console.print(ASCII_LOGO)
    console.print()
    console.print(Panel.fit("lazycommit", title="", subtitle="", style="cyan"))
    
    assert_repo()

    with console.status("[bold blue] detecting staged files...") as status:
        if stage_all:
            sp.run(["git", "add", "--update"], check=True)
        
        staged = get_staged_diff(exclude)
        if not staged:
            raise KnownError(
                "No staged changes found. Stage your changes manually, or automatically stage all changes with the `--all` flag."
            )

        # Check if diff is large
        is_large_diff = len(staged["diff"]) > 50000  # ~12.5k chars (~3k tokens)
        total_files = len(staged["files"])
        
        status.stop()
        
        if is_large_diff:
            console.print(f"detected {total_files} staged file{'s' if total_files != 1 else ''}:")
            for file in staged["files"]:
                console.print(f"     {file}")
            console.print("\n⚠️  Large diff detected - using chunked processing")
        else:
            console.print(f"📁 Detected {total_files} staged file{'s' if total_files != 1 else ''}:")
            for file in staged["files"]:
                console.print(f"     {file}")

    # Load configuration
    cfg = load({
        "generate": str(generate) if generate else None, 
        "type": commit_type or ""
    })

    # Generate commit messages
    with console.status("[bold blue] generating commit messages...") as status:
        if is_large_diff:
            # Try compact summary first for very large diffs
            compact = build_compact_summary(exclude, 25)
            if compact:
                msgs = generate_commit_message_from_summary(
                    cfg["GROQ_API_KEY"],
                    cfg["model"], 
                    cfg["locale"],
                    compact,
                    cfg["generate"],
                    cfg["max-length"],
                    cfg["type"],
                    cfg["timeout"],
                    cfg["proxy"]
                )
            else:
                msgs = generate_commit_message_from_chunks(
                    cfg["GROQ_API_KEY"],
                    cfg["model"],
                    cfg["locale"],
                    staged["diff"],
                    cfg["generate"],
                    cfg["max-length"],
                    cfg["type"],
                    cfg["timeout"],
                    cfg["proxy"],
                    cfg["chunk-size"]
                )
        else:
            msgs = generate_commit_message_from_chunks(
                cfg["GROQ_API_KEY"],
                cfg["model"],
                cfg["locale"],
                staged["diff"],
                cfg["generate"],
                cfg["max-length"],
                cfg["type"],
                cfg["timeout"],
                cfg["proxy"],
                cfg["chunk-size"]
            )
        status.stop()
        console.print("✅ Changes analyzed")

    if not msgs:
        raise KnownError("No commit messages were generated. Try again.")

    # Handle message selection
    if len(msgs) == 1:
        message = msgs[0]
        console.print(f"\n💬 Proposed commit message:")
        console.print(Panel(Text(message, style="bold white"), style="green"))
        
        if not Confirm.ask("Use this commit message?", default=True):
            console.print("❌ Commit cancelled")
            return 1
    else:
        console.print(f"\n💬 Pick a commit message to use:")
        for i, msg in enumerate(msgs, 1):
            console.print(f"  {i}. {msg}")
        
        choice = Prompt.ask(
            "Enter choice", 
            choices=[str(i) for i in range(1, len(msgs) + 1)],
            show_choices=True
        )
        message = msgs[int(choice) - 1]

    # Commit the changes
    sp.run(["git", "commit", "-m", message, *raw_git_args], check=True)
    console.print("✅ [green]Successfully committed![/green]")
    return 0