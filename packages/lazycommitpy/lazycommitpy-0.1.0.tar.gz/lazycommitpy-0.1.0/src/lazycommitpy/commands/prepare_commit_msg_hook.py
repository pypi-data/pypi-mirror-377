"""Prepare commit message hook implementation."""

from __future__ import annotations
import os
from rich.console import Console
from rich.panel import Panel
from ..utils.git import get_staged_diff
from ..utils.config import load
from ..utils.groq import generate_commit_message
from ..utils.error import KnownError

console = Console()


def run(message_file: str, commit_source: str | None) -> None:
    """Run prepare-commit-msg hook to auto-generate commit messages."""
    if not message_file:
        raise KnownError(
            "Commit message file path is missing. This file should be called from the 'prepare-commit-msg' git hook"
        )

    # If a commit message is passed in, ignore
    if commit_source:
        return
    
    # All staged files can be ignored by our filter
    staged = get_staged_diff([])
    if not staged:
        return
    
    try:
        console.print(Panel.fit("lazycommit", title="", subtitle="", style="cyan"))
        
        # Load config with environment variables
        env = os.environ
        cfg = load({
            "GROQ_API_KEY": env.get("GROQ_API_KEY"),
            "proxy": (
                env.get("https_proxy") or 
                env.get("HTTPS_PROXY") or 
                env.get("http_proxy") or 
                env.get("HTTP_PROXY")
            ),
        }, suppress=True)
        
        if not cfg:
            return
        
        with console.status("[bold blue]the generated commit messages..."):
            msgs = generate_commit_message(
                cfg["GROQ_API_KEY"],
                cfg["model"],
                cfg["locale"],
                staged["diff"],
                cfg["generate"],
                cfg["max-length"],
                cfg["type"],
                cfg["timeout"],
                cfg["proxy"]
            )
        
        if not msgs:
            return
        
        # Read existing commit message
        base_message = open(message_file, "r", encoding="utf-8").read()
        
        # When `--no-edit` is passed in, the base commit message is empty,
        # and even when you use pass in comments via #, they are ignored.
        supports_comments = base_message != ""
        has_multiple_messages = len(msgs) > 1
        
        instructions = ""
        
        if supports_comments:
            instructions = f"# AI generated commit{'s' if has_multiple_messages else ''}\n"
        
        if has_multiple_messages:
            if supports_comments:
                instructions += "# Select one of the following messages by uncommenting:\n"
            instructions += f"\n{chr(10).join(f'# {msg}' for msg in msgs)}"
        else:
            if supports_comments:
                instructions += "# Edit the message below and commit:\n"
            instructions += f"\n{msgs[0]}\n"
        
        with open(message_file, "a", encoding="utf-8") as f:
            f.write(instructions)
        
        console.print("✅ [green]Saved commit message![/green]")
    
    except Exception:
        # Silently fail in hook to avoid breaking git workflow
        pass