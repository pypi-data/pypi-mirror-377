#!/usr/bin/env python3

from typing import List, Optional, Tuple
import sys

import typer
from rich.console import Console

# Import logging module first
import logging

# Import necessary functions from utility modules
from roseApp.core.util import get_logger, TimeUtil, set_app_mode, AppMode, log_cli_error
from roseApp.cli.extract import extract as extract_main
from roseApp.cli.compress import compress as compress_main
from roseApp.cli.inspect import app as inspect_app
from roseApp.cli.data import app as data_app
# from roseApp.cli.plot import app as plot_app
from roseApp.cli.cache import app as cache_app

from roseApp.cli.load import load as load_main
from roseApp.cli.plugin import app as plugin_app
from roseApp.cli.interactive.run import app as run_app
# from roseApp.cli.profile import app as profile_app  # Temporarily disabled due to API migration
# from roseApp.tui.tui import app as tui_app

# Initialize logger
logger = get_logger("RoseCLI")
console = Console()
app = typer.Typer(help="ROS bag filter utility - A powerful tool for ROS bag manipulation")

def configure_logging(verbosity: int):
    """Configure logging level based on verbosity
    
    Args:
        verbosity: Number of 'v' flags (e.g., -vvv = 3)
    """
    levels = {
        0: logging.WARNING,  # Default
        1: logging.INFO,     # -v
        2: logging.DEBUG,    # -vv
        3: logging.DEBUG,    # -vvv (more details in formatter)
    }
    level = levels.get(min(verbosity, 3), logging.DEBUG)
    logger.setLevel(level)
    
    if verbosity >= 3:
        # Add more detailed format for high verbosity
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            ))

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase verbosity (e.g., -v, -vv, -vvv)"),
    profile: bool = typer.Option(False, "--profile", help="Enable performance profiling for analysis operations")
):
    """ROS bag filter utility - A powerful tool for ROS bag manipulation"""
    # Set application mode based on command
    if ctx.invoked_subcommand == "tui":
        set_app_mode(AppMode.TUI)
    else:
        set_app_mode(AppMode.CLI)
        
    configure_logging(verbose)
    
    # Set up profiling if requested
    if profile:
        from .core.cache import get_cache
        cache = get_cache()
        # cache.enable_profiling()  # Enable if profiling method exists
        logger.info("Performance profiling enabled")
    
    # If no subcommand is provided, start interactive mode
    if ctx.invoked_subcommand is None:
        from roseApp.cli.interactive.run import InteractiveRunner
        runner = InteractiveRunner()
        runner.run_interactive()
    



# Add subcommands
app.command(name="load")(load_main)
app.command(name="extract")(extract_main)
app.command(name="compress")(compress_main)
app.add_typer(inspect_app)
app.add_typer(data_app, name="data")
# app.add_typer(plot_app)
app.add_typer(cache_app)

app.add_typer(plugin_app, name="plugin")
app.add_typer(run_app, name="run")
# app.add_typer(profile_app)  # Temporarily disabled due to API migration
# app.add_typer(tui_app)

if __name__ == '__main__':
    try:
        app()
    except typer.Exit as e:
        # Re-raise typer.Exit cleanly (this is expected behavior)
        raise
    except Exception as e:
        # Handle top-level exceptions only in CLI mode
        if 'tui' not in sys.argv:
            error_msg = log_cli_error(e)
            typer.echo(error_msg, err=True)
            sys.exit(1)
        else:
            # Re-raise exceptions in TUI mode
            raise
