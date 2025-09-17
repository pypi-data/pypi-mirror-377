"""Run the data load job via CLI."""

import argparse
from pathlib import Path

from bblocks.datacommons_tools.cli.common import load_settings_from_args
from bblocks.datacommons_tools.gcp_utilities.pipeline import run_data_load

__all__ = ["add_parser", "run"]


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``dataload`` subcommand."""
    parser = subparsers.add_parser(
        "dataload", help="Run the Knowledge Graph data load job"
    )
    parser.add_argument(
        "--settings-file", type=Path, help="Path to the KG settings JSON file"
    )
    parser.add_argument(
        "--env-file", type=Path, help="Optional .env file containing KG settings"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=6000,
        help="Timeout for the job in seconds (default: %(default)s)",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Execute the ``dataload`` command."""
    settings = load_settings_from_args(args)
    run_data_load(settings=settings, timeout=args.timeout)
    return 0
