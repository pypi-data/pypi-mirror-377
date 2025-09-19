"""Main CLI entry point for lazycommit."""

import sys
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.traceback import install

from .commands.lazycommit import run as run_lazy
from .commands.hooks import install as hook_install, uninstall as hook_uninstall
from .commands.config import get_config, set_config
from .commands.prepare_commit_msg_hook import run as run_prepare
from .utils.error import KnownError

# Install rich traceback handler
install(show_locals=True)
console = Console()

app = typer.Typer(
    name="lazycommit",
    help="AI-powered Git commit message generator using Groq",
    add_completion=False,
    no_args_is_help=False,
)


@app.callback()
def main() -> None:
    """AI-powered Git commit message generator using Groq."""
    pass


@app.command("config")
def config(
    mode: Annotated[str, typer.Argument(help="get or set")],
    key_value: Annotated[list[str], typer.Argument()] = None,
) -> None:
    """Get or set configuration values."""
    try:
        if mode == "get":
            get_config(key_value or [])
            return
        if mode == "set":
            if not key_value:
                console.print("[red]Error: No key=value pairs provided[/red]")
                raise typer.Exit(code=1)
            pairs = []
            for kv in key_value:
                if "=" not in kv:
                    console.print(f"[red]Error: Invalid format '{kv}', expected key=value[/red]")
                    raise typer.Exit(code=1)
                pairs.append(tuple(kv.split("=", 1)))
            set_config(pairs)
            console.print("[green]✔ Configuration updated[/green]")
            return
        console.print(f"[red]Error: Invalid mode '{mode}', use 'get' or 'set'[/red]")
        raise typer.Exit(code=1)
    except KnownError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def hook(action: Annotated[str, typer.Argument(help="install or uninstall")]) -> None:
    """Install or uninstall git hooks."""
    try:
        if action == "install":
            hook_install()
            console.print("[green]✔ Hook installed[/green]")
            return
        if action == "uninstall":
            hook_uninstall()
            console.print("[green]✔ Hook uninstalled[/green]")
            return
        console.print(f"[red]Error: Invalid action '{action}', use 'install' or 'uninstall'[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("prepare-commit-msg", hidden=True)
def prepare(
    message_file: str,
    commit_source: str = typer.Argument(None),
    sha: str = typer.Argument(None),
) -> None:
    """Internal command for prepare-commit-msg hook."""
    run_prepare(message_file, commit_source)


@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    generate: Annotated[int, typer.Option("--generate", "-g", help="Number of commit messages to generate")] = None,
    exclude: Annotated[list[str], typer.Option("--exclude", "-x", help="Exclude files/patterns")] = None,
    all: Annotated[bool, typer.Option("--all", "-a", help="Stage all tracked files")] = False,
    type: Annotated[str, typer.Option("--type", "-t", help="Commit message type (conventional)")] = None,
    version: Annotated[bool, typer.Option("--version", help="Show version")] = False,
) -> None:
    """Generate AI-powered commit messages."""
    if version:
        console.print("lazycommitpy 0.1.0")
        return
    
    if ctx.invoked_subcommand is not None:
        return
    
    try:
        # Filter out our CLI args from raw git args
        raw_git_args = []
        skip_next = False
        for i, arg in enumerate(sys.argv[1:], 1):
            if skip_next:
                skip_next = False
                continue
            if arg in ["-g", "--generate", "-x", "--exclude", "-t", "--type"]:
                skip_next = True
                continue
            if arg in ["-a", "--all", "--version"]:
                continue
            if not arg.startswith("-"):
                continue
            raw_git_args.append(arg)
        
        sys.exit(run_lazy(generate, exclude or [], all, type, raw_git_args))
    except KnownError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


def entry() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    entry()
