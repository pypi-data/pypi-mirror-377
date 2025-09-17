#!/usr/bin/env python3
"""
CCC - Collective Context Commander Entry Point for pip/pipx installation
"""

import sys
import os
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

# Import all necessary modules and functions from ccc script
from ccc_manager import CCCManager
from ccc_commands import Commands

def is_claude_code_environment():
    """Detect if running in Claude Code environment"""
    # Check for explicit Claude Code markers first
    if os.environ.get('CLAUDE_CODE') == '1':
        return True

    # Check for known terminal environments (these are NOT Claude Code)
    terminal_indicators = [
        os.environ.get('TERM_PROGRAM'),  # tmux, screen, etc.
        os.environ.get('SSH_CLIENT'),     # SSH session
        os.environ.get('SSH_TTY'),        # SSH TTY
    ]
    if any(terminal_indicators):
        return False

    # Check for terminal types that indicate real terminals
    term = os.environ.get('TERM', '')
    if any(term.startswith(prefix) for prefix in ['tmux', 'screen', 'xterm', 'rxvt', 'gnome']):
        return False

    # Check for dumb terminal or completely missing TTY (likely Claude Code)
    if (os.environ.get('TERM') == 'dumb' or
        (not sys.stdout.isatty() and os.environ.get('TERM_PROGRAM') is None)):
        return True

    # Default: assume terminal environment if we have a TTY
    return not sys.stdout.isatty()

def print_compact_usage():
    """Print compact usage information for Claude Code"""
    print("""
CCC - Collective Context Commander Plugin
Usage: ccc <command> [service] [options]

[CORE]: status, config, list, help
[CONTROL]: start, restart, stop, test, exec
[SERVICES]: autoinput, save, dialog
[COMM]: ccc (read), ccc -r, ccc -w

Quick Examples:
  ccc list                   # Show all services
  ccc status save            # Check save status
  ccc start autoinput -t=3   # Start autoinput (3min)
  ccc start save -d          # Start logging + dialog
  ccc                        # Read other Claude messages

Help Options:
  ccc help full              # Detailed help with all sections
  ccc help core              # Core commands only
  ccc help control           # Service control commands
  ccc help services          # Specialized services
  ccc help communication     # Claude communication
  ccc help options           # Command options
  ccc help examples          # Usage examples

TIP: Partial names work! (e.g., 'ccc help comm' for communication)
""")

def main():
    """Entry point for pip/pipx installation - direct Python implementation"""
    import sys

    # Initialize CCC manager and commands
    manager = CCCManager()
    commands = Commands(manager)

    # Handle no arguments - show help
    if len(sys.argv) <= 1:
        print("CCC Commander (cccmd) v0.3.2 - Multi-Agent AI Orchestration")
        print("\nVerfügbare Commands:")
        print("  version          - Zeige Version")
        print("  help             - Zeige diese Hilfe")
        print("  context          - Context Management")
        print("  session          - Session Management")
        print("\nFür detaillierte Hilfe siehe: https://collective-context.org/ccc/")
        return 0

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    try:
        # Route commands to appropriate handlers
        if command in ['help', 'h', '--help']:
            print("CCC Commander (cccmd) v0.3.2 - Multi-Agent AI Orchestration")
            print("\nVerfügbare Commands:")
            print("  version          - Zeige Version")
            print("  help             - Zeige diese Hilfe")
            print("  context          - Context Management")
            print("  session          - Session Management")
            print("\nFür detaillierte Hilfe siehe: https://collective-context.org/ccc/")
            return 0
        elif command == 'version':
            print("CCC Commander (cccmd) v0.3.2")
        elif command in ['context', 'co']:
            if args:
                commands.handle_context_command(args)
            else:
                commands.handle_context_command([])
        elif command in ['session', 'ses']:
            if args:
                commands.handle_session_command(args)
            else:
                commands.handle_session_command([])
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'cccmd help' for available commands")
            return 1

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())