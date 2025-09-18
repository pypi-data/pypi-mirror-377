"""Main entry point for juno-agent."""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .config import ConfigManager
from .ui import WizardApp
from .utils import SystemStatus

app = typer.Typer(
    name="juno-agent",
    help="A Python CLI tool to help developers setup their libraries in AI coding tools",
    add_completion=True,
)

console = Console()


def initialize_tracing() -> None:
    """Initialize Phoenix tracing with environment configuration."""
    try:
        from phoenix.otel import register
        
        # Get configuration from environment variables
        project_name = os.getenv("PHOENIX_PROJECT_NAME", "juno-cli")
        endpoint = os.getenv("PHOENIX_ENDPOINT", "https://app.phoenix.arize.com/v1/traces")
        
        # Register Phoenix tracing
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
            auto_instrument=True
        )
        
        console.print(f"[green]✅ Phoenix tracing initialized[/green]")
        console.print(f"[dim]Project: {project_name}[/dim]")
        console.print(f"[dim]Endpoint: {endpoint}[/dim]")
        
        return tracer_provider
        
    except ImportError:
        console.print(f"[red]❌ Phoenix tracing not available. Install with: pip install arize-phoenix-otel[/red]")
        console.print(f"[yellow]Continuing without tracing...[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize Phoenix tracing: {e}[/red]")
        console.print(f"[yellow]Continuing without tracing...[/yellow]")
        return None


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    workdir: Optional[Path] = typer.Option(
        None,
        "--workdir",
        "-w",
        help="Working directory (defaults to current directory)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
    trace: bool = typer.Option(
        False,
        "--trace",
        help="Enable Phoenix tracing (requires arize-phoenix package)",
    ),
    debug_litellm: bool = typer.Option(
        False,
        "--debug-litellm",
        help="Enable LiteLLM debug mode for detailed API request/response logging",
    ),
    ui_mode: Optional[str] = typer.Option(
        None,
        "--ui-mode",
        help="UI mode: 'simple' or 'fancy' (defaults to config setting)",
    ),
) -> None:
    """Start the juno-agent interactive interface."""
    # Initialize tracing first if requested
    if trace:
        initialize_tracing()
    
    # Enable LiteLLM debug mode if requested
    if debug_litellm:
        try:
            import litellm
            litellm._turn_on_debug()
            console.print("[green]✅ LiteLLM debug mode enabled[/green]")
        except ImportError:
            console.print("[red]❌ LiteLLM not available for debug mode[/red]")
        except Exception as e:
            console.print(f"[red]❌ Failed to enable LiteLLM debug mode: {e}[/red]")
    
    if ctx.invoked_subcommand is not None:
        return
        
    if workdir is None:
        workdir = Path.cwd()
    
    workdir = workdir.resolve()
    
    if not workdir.exists() or not workdir.is_dir():
        console.print(f"[red]Error: Directory {workdir} does not exist[/red]")
        raise typer.Exit(1)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(workdir)
        
        # Override UI mode if specified via command line
        if ui_mode:
            from .config import UIMode
            if ui_mode.lower() == 'fancy':
                config = config_manager.load_config()
                config.ui_mode = UIMode.FANCY
                config_manager.save_config(config)
            elif ui_mode.lower() == 'simple':
                config = config_manager.load_config()
                config.ui_mode = UIMode.SIMPLE
                config_manager.save_config(config)
            else:
                console.print(f"[red]Invalid UI mode: {ui_mode}. Use 'simple' or 'fancy'.[/red]")
                raise typer.Exit(1)
        
        # Check system status
        system_status = SystemStatus(workdir)
        
        # Start the wizard application
        wizard_app = WizardApp(config_manager, system_status, debug=debug)
        wizard_app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    console.print(f"juno-agent version {__version__}")


@app.command() 
def status(
    workdir: Optional[Path] = typer.Option(
        None,
        "--workdir", 
        "-w",
        help="Working directory (defaults to current directory)",
    )
) -> None:
    """Show current status of the workspace."""
    if workdir is None:
        workdir = Path.cwd()
        
    workdir = workdir.resolve()
    system_status = SystemStatus(workdir)
    
    # Display status in a panel
    status_info = system_status.get_status_info()
    
    console.print(Panel.fit(
        f"""[bold]Workspace Status[/bold]
        
[blue]Working Directory:[/blue] {status_info['workdir']}
[blue]Git Repository:[/blue] {status_info['git_status']}
[blue]API Key:[/blue] {status_info['api_key_status']}
[blue]Editor:[/blue] {status_info['editor']}""",
        title="juno-agent",
        border_style="blue",
    ))


@app.command()
def setup(
    workdir: Optional[Path] = typer.Option(
        None,
        "--workdir",
        "-w", 
        help="Working directory (defaults to current directory)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
    trace: bool = typer.Option(
        False,
        "--trace",
        help="Enable Phoenix tracing (requires arize-phoenix package)",
    ),
    debug_litellm: bool = typer.Option(
        False,
        "--debug-litellm",
        help="Enable LiteLLM debug mode for detailed API request/response logging",
    ),
    verify_only: bool = typer.Option(
        False,
        "--verify-only",
        help="Run only setup verification, skip full setup process",
    ),
    docs_only: bool = typer.Option(
        False,
        "--docs-only", 
        help="Run intelligent dependency resolver to scan and fetch documentation",
    ),
    headless: bool = typer.Option(
        False,
        "--headless",
        help="Run setup steps without launching the TUI (generate JUNO.md & AGENTS.md, then verify)",
    ),
    headless_fetch_docs: bool = typer.Option(
        False,
        "--headless-fetch-docs",
        help="In headless mode, run the Agentic Dependency Resolver to fetch docs into external_context",
    ),
    # Headless installs MCP by default (no extra flag to keep UX simple)
    report_file: Optional[Path] = typer.Option(
        None,
        "--report-file",
        help="When in headless mode, write the verification report markdown to this path",
    ),
    editor: Optional[str] = typer.Option(
        None,
        "--editor",
        help="Optional IDE/editor name for headless mode (e.g., 'claude_code', 'cursor', 'windsurf')",
    ),
    ui_mode: Optional[str] = typer.Option(
        None,
        "--ui-mode", 
        help="UI mode: 'simple' or 'fancy' (defaults to config setting)"
    ),
) -> None:
    """Launch the setup wizard or run verification only. Uses configured UI mode unless overridden."""
    # Initialize tracing first if requested
    if trace:
        initialize_tracing()
        # Set environment variables for TinyAgent tracing integration
        os.environ["JUNO_TRACING_ENABLED"] = "1"
        os.environ["OTEL_TRACES_EXPORTER"] = "phoenix"
    
    # Enable LiteLLM debug mode if requested
    if debug_litellm:
        try:
            import litellm
            litellm._turn_on_debug()
            console.print("[green]✅ LiteLLM debug mode enabled[/green]")
        except ImportError:
            console.print("[red]❌ LiteLLM not available for debug mode[/red]")
        except Exception as e:
            console.print(f"[red]❌ Failed to enable LiteLLM debug mode: {e}[/red]")
    
    # Validate flags - verify_only is exclusive with others
    if verify_only and docs_only:
        console.print("[red]Error: --verify-only cannot be used with --docs-only[/red]")
        raise typer.Exit(1)
    
    if workdir is None:
        workdir = Path.cwd()
    
    workdir = workdir.resolve()
    
    if not workdir.exists() or not workdir.is_dir():
        console.print(f"[red]Error: Directory {workdir} does not exist[/red]")
        raise typer.Exit(1)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(workdir)
        
        # Override UI mode if specified via command line
        if ui_mode:
            from .config import UIMode
            if ui_mode.lower() == 'fancy':
                config = config_manager.load_config()
                config.ui_mode = UIMode.FANCY
                config_manager.save_config(config)
            elif ui_mode.lower() == 'simple':
                config = config_manager.load_config()
                config.ui_mode = UIMode.SIMPLE
                config_manager.save_config(config)
            else:
                console.print(f"[red]Invalid UI mode: {ui_mode}. Use 'simple' or 'fancy'.[/red]")
                raise typer.Exit(1)
        
        if headless:
            # Unified headless path via shared pipeline
            from .setup.pipeline import run_setup_pipeline
            dbg = config_manager.create_debug_logger(debug=True)
            selected_editor = editor or (config_manager.load_config().editor or "Claude Code")
            result = run_setup_pipeline(
                workdir=Path(workdir),
                config_manager=config_manager,
                editor_display=("Claude Code" if selected_editor.lower() in ("claude_code", "claude code") else selected_editor),
                logger=dbg,
                report_file=Path(report_file) if report_file else None,
                textual_ui_callback=None,
            )
            console.print(f"[bold]Headless Setup Verification[/bold]")
            console.print(f"PASS: {result['pass']}  FAIL: {result['fail']}  WARN: {result['warn']}  INFO: {result['info']}")
            if report_file:
                console.print(f"\n[green]Report written to {report_file}[/green]")
            return
        
        # Load config without forcing UI mode
        
        # Check system status
        system_status = SystemStatus(workdir)
        
        # Start the wizard application with appropriate mode
        if verify_only:
            wizard_app = WizardApp(config_manager, system_status, debug=debug, verify_only_mode=True)
        elif docs_only:
            # --docs-only runs intelligent dependency resolver ONLY
            wizard_app = WizardApp(config_manager, system_status, debug=debug, agentic_resolver_mode=True)
        else:
            wizard_app = WizardApp(config_manager, system_status, debug=debug, auto_start_setup=True)
        wizard_app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
