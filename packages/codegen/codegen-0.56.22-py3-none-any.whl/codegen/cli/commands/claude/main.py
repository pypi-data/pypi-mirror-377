"""Claude Code command with session tracking."""

import json
import os
import signal
import subprocess
import sys
import time

import requests
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel

from codegen.cli.api.endpoints import API_ENDPOINT
from codegen.cli.auth.token_manager import get_current_token
from codegen.cli.commands.claude.claude_log_watcher import ClaudeLogWatcherManager
from codegen.cli.commands.claude.claude_session_api import (
    create_claude_session,
    generate_session_id,
    update_claude_session_status,
)
from codegen.cli.commands.claude.config.mcp_setup import add_codegen_mcp_server, cleanup_codegen_mcp_server
from codegen.cli.commands.claude.hooks import SESSION_FILE, cleanup_claude_hook, ensure_claude_hook, get_codegen_url
from codegen.cli.commands.claude.quiet_console import console
from codegen.cli.commands.claude.utils import resolve_claude_path
from codegen.cli.rich.spinners import create_spinner
from codegen.cli.utils.org import resolve_org_id
from codegen.cli.utils.repo import resolve_repo_id
from codegen.shared.logging.get_logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def _get_session_context() -> dict:
    """Get session context for logging."""
    try:
        from codegen.cli.telemetry.otel_setup import get_session_uuid

        return {"session_id": get_session_uuid()}
    except ImportError:
        return {}


t_console = Console()


def _run_claude_background(resolved_org_id: int, prompt: str | None) -> None:
    """Create a background agent run with Claude context and exit."""
    logger.info(
        "Claude background run started",
        extra={"operation": "claude.background", "org_id": resolved_org_id, "prompt_length": len(prompt) if prompt else 0, "command": "codegen claude --background", **_get_session_context()},
    )

    start_time = time.time()
    token = get_current_token()
    if not token:
        logger.error(
            "Claude background run failed - not authenticated", extra={"operation": "claude.background", "org_id": resolved_org_id, "error_type": "not_authenticated", **_get_session_context()}
        )
        console.print("[red]Error:[/red] Not authenticated. Please run 'codegen login' first.")
        raise typer.Exit(1)

    payload = {"prompt": prompt or "Start a Claude Code background session"}

    spinner = create_spinner("Creating agent run...")
    spinner.start()
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-codegen-client": "codegen__claude_code",
        }
        url = f"{API_ENDPOINT.rstrip('/')}/v1/organizations/{resolved_org_id}/agent/run"
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        agent_run_data = response.json()

        duration_ms = (time.time() - start_time) * 1000
        run_id = agent_run_data.get("id", "Unknown")
        status = agent_run_data.get("status", "Unknown")

        logger.info(
            "Claude background run created successfully",
            extra={"operation": "claude.background", "org_id": resolved_org_id, "agent_run_id": run_id, "status": status, "duration_ms": duration_ms, "success": True, **_get_session_context()},
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Claude background run failed",
            extra={
                "operation": "claude.background",
                "org_id": resolved_org_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration_ms": duration_ms,
                "success": False,
                **_get_session_context(),
            },
            exc_info=True,
        )
        raise
    finally:
        spinner.stop()

    run_id = agent_run_data.get("id", "Unknown")
    status = agent_run_data.get("status", "Unknown")
    web_url = agent_run_data.get("web_url", "")

    result_lines = [
        f"[cyan]Agent Run ID:[/cyan] {run_id}",
        f"[cyan]Status:[/cyan]       {status}",
    ]
    if web_url:
        result_lines.append(f"[cyan]Web URL:[/cyan]      {web_url}")

    t_console.print(
        Panel(
            "\n".join(result_lines),
            title="🤖 [bold]Background Agent Run Created[/bold]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    t_console.print("\n[dim]💡 Track progress with:[/dim] [cyan]codegen agents[/cyan]")
    if web_url:
        t_console.print(f"[dim]🌐 View in browser:[/dim]  [link]{web_url}[/link]")


def _run_claude_interactive(resolved_org_id: int, no_mcp: bool | None) -> None:
    """Launch Claude Code with session tracking and log watching."""
    # Generate session ID for tracking
    session_id = generate_session_id()

    logger.info(
        "Claude interactive session started",
        extra={"operation": "claude.interactive", "org_id": resolved_org_id, "claude_session_id": session_id, "mcp_disabled": bool(no_mcp), "command": "codegen claude", **_get_session_context()},
    )

    console.print(f"🆔 Generated session ID: {session_id[:8]}...", style="dim")

    console.print("🚀 Starting Claude Code with session tracking...", style="blue")
    console.print(f"🎯 Organization ID: {resolved_org_id}", style="dim")

    # Set up environment variables for hooks to access session information
    os.environ["CODEGEN_CLAUDE_SESSION_ID"] = session_id
    os.environ["CODEGEN_CLAUDE_ORG_ID"] = str(resolved_org_id)

    # Proactively create the backend session as a fallback in case hooks fail
    try:
        agent_run_id = create_claude_session(session_id, resolved_org_id)
        if agent_run_id:
            console.print("✅ Backend session created", style="green")
        else:
            console.print("⚠️  Could not create backend session at startup (will rely on hooks)", style="yellow")
    except Exception as e:
        agent_run_id = None
        console.print(f"⚠️  Session creation error at startup: {e}", style="yellow")

    # Set up Claude hook for session tracking
    if not ensure_claude_hook():
        console.print("⚠️  Failed to set up session tracking hook", style="yellow")

    # Write session context file for downstream hooks and tools (after hook setup)
    try:
        SESSION_FILE.parent.mkdir(exist_ok=True)
        session_payload = {
            "session_id": session_id,
            "agent_run_id": agent_run_id,
            "org_id": resolved_org_id,
            "hook_event": "Startup",
        }
        with open(SESSION_FILE, "w") as f:
            json.dump(session_payload, f, indent=2)
            f.write("\n")
        console.print("📝 Wrote session file to ~/.codegen/claude-session.json", style="dim")
    except Exception as e:
        console.print(f"⚠️  Could not write session file: {e}", style="yellow")

    # Initialize log watcher manager
    log_watcher_manager = ClaudeLogWatcherManager()

    # Resolve Claude CLI path and test accessibility
    claude_path = resolve_claude_path()
    if not claude_path:
        logger.error(
            "Claude CLI not found",
            extra={"operation": "claude.interactive", "org_id": resolved_org_id, "claude_session_id": session_id, "error_type": "claude_cli_not_found", **_get_session_context()},
        )
        console.print("❌ Claude Code CLI not found.", style="red")
        console.print(
            "💡 If you migrated a local install, ensure `~/.claude/local/claude` exists, or add it to PATH.",
            style="dim",
        )
        console.print(
            "💡 Otherwise install globally via npm (e.g., `npm i -g claude`) or run `claude /migrate`.",
            style="dim",
        )
        update_claude_session_status(session_id, "ERROR", resolved_org_id)
        raise typer.Exit(1)

    console.print(f"🔍 Using Claude CLI at: {claude_path}", style="blue")
    try:
        test_result = subprocess.run([claude_path, "--version"], capture_output=True, text=True, timeout=10)
        if test_result.returncode == 0:
            console.print(f"✅ Claude Code found: {test_result.stdout.strip()}", style="green")
        else:
            console.print(f"⚠️  Claude Code test failed with code {test_result.returncode}", style="yellow")
            if test_result.stderr:
                console.print(f"Error: {test_result.stderr.strip()}", style="red")
    except subprocess.TimeoutExpired:
        console.print("⚠️  Claude Code version check timed out", style="yellow")
    except Exception as e:
        console.print(f"⚠️  Claude Code test error: {e}", style="yellow")

    # If MCP endpoint provided, register MCP server via Claude CLI before launch
    if not no_mcp:
        # Resolve repository ID if available
        repo_id = resolve_repo_id()
        if repo_id:
            console.print(f"🎯 Repository ID: {repo_id}", style="dim")
        add_codegen_mcp_server(org_id=resolved_org_id, repo_id=repo_id)

    console.print("🔵 Starting Claude Code session...", style="blue")

    try:
        # Launch Claude Code with our session ID
        console.print(f"🚀 Launching Claude Code with session ID: {session_id[:8]}...", style="blue")

        url = get_codegen_url(session_id)
        console.print(f"\n🔵 Codegen URL: {url}\n", style="bold blue")

        process = subprocess.Popen([claude_path, "--session-id", session_id])

        # Start log watcher for the session
        console.print("📋 Starting log watcher...", style="blue")
        log_watcher_started = log_watcher_manager.start_watcher(
            session_id=session_id,
            org_id=resolved_org_id,
            poll_interval=1.0,
            on_log_entry=None,
        )

        if not log_watcher_started:
            console.print("⚠️  Failed to start log watcher", style="yellow")

        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            console.print("\n🛑 Stopping Claude Code...", style="yellow")
            log_watcher_manager.stop_all_watchers()
            process.terminate()
            cleanup_claude_hook()
            cleanup_codegen_mcp_server()
            update_claude_session_status(session_id, "COMPLETE", resolved_org_id)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Wait for Claude Code to finish
        returncode = process.wait()

        # Handle session completion based on exit code
        session_status = "COMPLETE" if returncode == 0 else "ERROR"
        update_claude_session_status(session_id, session_status, resolved_org_id)

        if returncode != 0:
            logger.error(
                "Claude interactive session failed",
                extra={
                    "operation": "claude.interactive",
                    "org_id": resolved_org_id,
                    "claude_session_id": session_id,
                    "exit_code": returncode,
                    "session_status": session_status,
                    **_get_session_context(),
                },
            )
            console.print(f"❌ Claude Code exited with error code {returncode}", style="red")
        else:
            logger.info(
                "Claude interactive session completed successfully",
                extra={
                    "operation": "claude.interactive",
                    "org_id": resolved_org_id,
                    "claude_session_id": session_id,
                    "exit_code": returncode,
                    "session_status": session_status,
                    **_get_session_context(),
                },
            )
            console.print("✅ Claude Code finished successfully", style="green")

    except FileNotFoundError:
        logger.error(
            "Claude Code executable not found",
            extra={"operation": "claude.interactive", "org_id": resolved_org_id, "claude_session_id": session_id, "error_type": "claude_executable_not_found", **_get_session_context()},
        )
        console.print("❌ Claude Code not found. Please install Claude Code first.", style="red")
        console.print("💡 Visit: https://claude.ai/download", style="dim")
        log_watcher_manager.stop_all_watchers()
        update_claude_session_status(session_id, "ERROR", resolved_org_id)
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger.info(
            "Claude interactive session interrupted by user",
            extra={
                "operation": "claude.interactive",
                "org_id": resolved_org_id,
                "claude_session_id": session_id,
                "session_status": "CANCELLED",
                "exit_reason": "user_interrupt",
                **_get_session_context(),
            },
        )
        console.print("\n🛑 Interrupted by user", style="yellow")
        log_watcher_manager.stop_all_watchers()
        update_claude_session_status(session_id, "CANCELLED", resolved_org_id)
    except Exception as e:
        logger.error(
            "Claude interactive session error",
            extra={
                "operation": "claude.interactive",
                "org_id": resolved_org_id,
                "claude_session_id": session_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "session_status": "ERROR",
                **_get_session_context(),
            },
            exc_info=True,
        )
        console.print(f"❌ Error running Claude Code: {e}", style="red")
        log_watcher_manager.stop_all_watchers()
        update_claude_session_status(session_id, "ERROR", resolved_org_id)
        raise typer.Exit(1)
    finally:
        # Clean up resources
        try:
            log_watcher_manager.stop_all_watchers()
        except Exception as e:
            console.print(f"⚠️  Error stopping log watchers: {e}", style="yellow")

        cleanup_claude_hook()

        # Show final session info
        url = get_codegen_url(session_id)
        console.print(f"\n🔵 Session URL: {url}", style="bold blue")
        console.print(f"🆔 Session ID: {session_id}", style="dim")
        console.print(f"🎯 Organization ID: {resolved_org_id}", style="dim")
        console.print("💡 Check your backend to see the session data", style="dim")


def claude(
    org_id: int | None = typer.Option(None, help="Organization ID (defaults to CODEGEN_ORG_ID/REPOSITORY_ORG_ID or auto-detect)"),
    no_mcp: bool | None = typer.Option(False, "--no-mcp", help="Disable Codegen's MCP server with additional capabilities over HTTP"),
    background: str | None = typer.Option(None, "--background", "-b", help="Create a background agent run with this prompt instead of launching Claude Code"),
):
    """Run Claude Code with session tracking or create a background run."""
    logger.info(
        "Claude command invoked",
        extra={
            "operation": "claude.command",
            "org_id": org_id,
            "no_mcp": bool(no_mcp),
            "is_background": background is not None,
            "background_prompt_length": len(background) if background else 0,
            "command": f"codegen claude{' --background' if background else ''}",
            **_get_session_context(),
        },
    )

    # Resolve org_id early for session management
    resolved_org_id = resolve_org_id(org_id)
    if resolved_org_id is None:
        logger.error("Claude command failed - no org ID", extra={"operation": "claude.command", "error_type": "org_id_missing", **_get_session_context()})
        console.print("[red]Error:[/red] Organization ID not provided. Pass --org-id, set CODEGEN_ORG_ID, or REPOSITORY_ORG_ID.")
        raise typer.Exit(1)

    try:
        if background is not None:
            # Use the value from --background as the prompt
            final_prompt = background
            _run_claude_background(resolved_org_id, final_prompt)
            return

        _run_claude_interactive(resolved_org_id, no_mcp)

    except typer.Exit:
        # Let typer exits pass through without additional logging
        raise
    except Exception as e:
        logger.error(
            "Claude command failed unexpectedly",
            extra={
                "operation": "claude.command",
                "org_id": resolved_org_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "is_background": background is not None,
                **_get_session_context(),
            },
            exc_info=True,
        )
        raise
