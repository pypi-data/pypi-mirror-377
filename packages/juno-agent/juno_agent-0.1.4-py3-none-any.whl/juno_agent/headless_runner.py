"""Headless runner for non-interactive mode."""

import asyncio
import time
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigManager
from .tiny_agent import TinyCodeAgentChat, TinyCodeAgentManager


class HeadlessRunner:
    """Handles headless (non-interactive) execution of juno-agent."""

    def __init__(self, config_manager: ConfigManager, debug: bool = False):
        self.config_manager = config_manager
        self.debug = debug
        self.console = Console()
        self.tiny_manager = TinyCodeAgentManager(config_manager)
        self.tiny_code_agent = TinyCodeAgentChat(
            config_manager,
            debug=self.debug,
            console=self.console
        )

    async def run(self, message: str) -> None:
        """Run the agent in headless mode with the provided message."""
        # Check if TinyAgent can be initialized
        status = self.tiny_manager.check_requirements()

        if not status["can_initialize"]:
            self.console.print("[red]❌ Cannot initialize Juno Agent[/red]")
            status_info = self.tiny_manager.get_status_info()

            # Debug: print the full status information
            if self.debug:
                self.console.print(f"[dim]Debug - Full status: {status}[/dim]")
                self.console.print(f"[dim]Debug - Status info: {status_info}[/dim]")

            # Show issues if available
            issues = status_info.get("issues", [])
            if issues:
                for issue in issues:
                    self.console.print(f"   • {issue}")
            else:
                # Show general status information
                for key, value in status_info.items():
                    if key != "issues":
                        status_mark = "✅" if value else "❌"
                        self.console.print(f"   • {key.replace('_', ' ').title()}: {status_mark}")

            raise RuntimeError("Juno Agent initialization failed")

        try:
            # Initialize the agent
            await self.tiny_code_agent.initialize_agent()

            # Get model display name
            config = self.config_manager.load_config()
            agent_config = config.agent_config

            if agent_config and agent_config.model_slug:
                model_display = agent_config.model_slug.upper()
            elif agent_config and agent_config.model_name:
                model_display = agent_config.model_name.split("/")[-1].upper()
            else:
                model_display = "AGENT"

            # Process the message with progress indicator
            response = None
            error = None

            async def process_message():
                nonlocal response, error
                try:
                    response = await self.tiny_code_agent.process_chat_message(message)
                except Exception as e:
                    error = e

            # Show progress with elapsed time
            start_time = time.time()
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold cyan]🤖 {model_display} processing...[/bold cyan]"),
                TextColumn("[dim]"),
                console=self.console,
                transient=True,
                refresh_per_second=10
            ) as progress:
                task = progress.add_task("Processing", total=None)

                # Run the processing in background
                process_task = asyncio.create_task(process_message())

                # Wait for completion with progress updates
                while not process_task.done():
                    elapsed = int(time.time() - start_time)
                    progress.update(task, description=f"[bold cyan]🤖 {model_display} processing...[/bold cyan] [dim]{elapsed}s[/dim]")
                    await asyncio.sleep(0.1)

                await process_task

            # Handle the result
            if error:
                self.console.print(f"[red]❌ Error: {str(error)}[/red]")
                raise error

            # Display the response
            self.console.print()
            self.console.print(response)

        except Exception as e:
            if self.debug:
                self.console.print_exception()
            else:
                self.console.print(f"[red]❌ Error: {str(e)}[/red]")
            raise