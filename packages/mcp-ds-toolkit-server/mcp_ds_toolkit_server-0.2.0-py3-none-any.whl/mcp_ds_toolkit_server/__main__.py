"""
MCP Data Science Toolkit - Main Entry Point

This module provides the main entry point for the MCP Data Science Toolkit server,
handling command-line interface initialization, logging setup, and server startup.

The module supports both direct execution and programmatic usage, providing
flexible deployment options for different environments and use cases.

Functions:
    run_server: Async function to run the server with optional settings
    cli_main: CLI entry point for command-line execution

Example:
    Run the server directly from command line::

        python -m mcp_ds_toolkit --artifacts-dir ./my_artifacts

    Or programmatically::

        from mcp_ds_toolkit_server.__main__ import run_server
        import asyncio

        asyncio.run(run_server())
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from mcp_ds_toolkit_server.server import main
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import setup_logging


async def run_server(settings: Optional[Settings] = None) -> None:
    """Run the MCP Data Science Toolkit server.

    Initializes and starts the server with proper logging configuration
    and error handling. This function can be used for programmatic
    server startup in custom deployment scenarios.

    Args:
        settings (Optional[Settings]): Configuration settings for the server.
            If None, creates a new Settings instance with default values.

    Note:
        This function is the primary async entry point for server execution
        and should be called within an asyncio event loop.
    """
    if settings is None:
        settings = Settings()

    # Set up logging
    setup_logging(settings)

    # Run the server
    await main()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="MCP Data Science Toolkit Server")
    parser.add_argument(
        "--artifacts-dir",
        type=str,
        default="./artifacts",
        help="Base directory for ML artifacts storage (default: ./artifacts)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)",
    )
    return parser.parse_args()


def cli_main() -> None:
    """CLI entry point for the MCP Data Science Toolkit server.

    Handles command-line execution of the server with proper error handling
    and graceful shutdown on keyboard interrupt. This function provides
    the standard entry point for running the server from the command line.

    The function handles:
        - Command-line argument parsing
        - Artifacts directory validation and setup
        - Asyncio event loop management
        - Graceful shutdown on Ctrl+C
        - Error logging and appropriate exit codes

    Exit Codes:
        0: Normal shutdown (user interrupt)
        1: Error during server execution
    """
    # Parse command line arguments
    args = parse_args()

    # Validate and setup artifacts directory
    artifacts_dir = Path(args.artifacts_dir).resolve()
    if not artifacts_dir.exists():
        try:
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created artifacts directory: {artifacts_dir}")
        except Exception as e:
            print(f"Error: Cannot create artifacts directory {artifacts_dir}: {e}")
            sys.exit(1)

    if not artifacts_dir.is_dir():
        print(f"Error: Artifacts path is not a directory: {artifacts_dir}")
        sys.exit(1)

    # Create settings with artifacts directory
    settings = Settings()
    settings.data_dir = artifacts_dir / "data"
    settings.models_dir = artifacts_dir / "models"
    settings.experiments_dir = artifacts_dir / "experiments"
    settings.workspace_path = artifacts_dir / "workspace"
    settings.log_level = args.log_level

    logger = logging.getLogger(__name__)

    try:
        asyncio.run(run_server(settings))
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
