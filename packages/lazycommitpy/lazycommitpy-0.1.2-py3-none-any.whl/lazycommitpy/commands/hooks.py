"""Git hooks management."""

from __future__ import annotations
import os
import stat
import subprocess as sp
from pathlib import Path
from rich.console import Console
from ..utils.error import KnownError

console = Console()

HOOK_NAME = "prepare-commit-msg"


def install() -> None:
    """Install the prepare-commit-msg git hook."""
    try:
        # Get git repository root
        result = sp.run(
            ["git", "rev-parse", "--git-dir"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        git_dir = result.stdout.strip()
        
        # Create hooks directory if it doesn't exist
        hooks_dir = Path(git_dir) / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        hook_path = hooks_dir / HOOK_NAME
        
        # Check if hook already exists
        if hook_path.exists():
            try:
                # Check if it's our hook by reading content
                content = hook_path.read_text()
                if "lazycommit prepare-commit-msg" in content:
                    console.print("⚠️  The hook is already installed")
                    return
                else:
                    raise KnownError(
                        f"A different {HOOK_NAME} hook seems to be installed. "
                        "Please remove it before installing lazycommit."
                    )
            except Exception:
                raise KnownError(
                    f"A different {HOOK_NAME} hook seems to be installed. "
                    "Please remove it before installing lazycommit."
                )
        
        # Create the hook script
        is_windows = os.name == 'nt'
        
        if is_windows:
            # Windows batch script
            script_content = f"""#!/usr/bin/env python
import subprocess
import sys
subprocess.run([sys.executable, "-m", "lazycommitpy.cli", "prepare-commit-msg"] + sys.argv[1:])
"""
        else:
            # Unix shell script
            script_content = f"""#!/bin/sh
lazycommit prepare-commit-msg "$1" "$2" "$3"
"""
        
        # Write the hook
        hook_path.write_text(script_content)
        
        # Make executable on Unix systems
        if not is_windows:
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        
        console.print("✅ [green]Hook installed[/green]")
        
    except sp.CalledProcessError:
        raise KnownError("Not in a git repository")
    except Exception as e:
        raise KnownError(f"Failed to install hook: {e}")


def uninstall() -> None:
    """Uninstall the prepare-commit-msg git hook."""
    try:
        # Get git repository root
        result = sp.run(
            ["git", "rev-parse", "--git-dir"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        git_dir = result.stdout.strip()
        
        hook_path = Path(git_dir) / "hooks" / HOOK_NAME
        
        if not hook_path.exists():
            console.print("⚠️  Hook is not installed")
            return
        
        try:
            # Verify it's our hook before removing
            content = hook_path.read_text()
            if "lazycommit prepare-commit-msg" not in content and "lazycommitpy.cli" not in content:
                console.print("⚠️  Hook is not installed")
                return
        except Exception:
            console.print("⚠️  Hook is not installed")
            return
        
        # Remove the hook
        hook_path.unlink()
        console.print("✅ [green]Hook uninstalled[/green]")
        
    except sp.CalledProcessError:
        raise KnownError("Not in a git repository")
    except Exception as e:
        raise KnownError(f"Failed to uninstall hook: {e}")