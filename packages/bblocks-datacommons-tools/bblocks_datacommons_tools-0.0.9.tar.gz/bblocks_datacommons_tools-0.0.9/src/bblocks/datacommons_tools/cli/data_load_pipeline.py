"""Run the full Knowledge Graph pipeline via CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from bblocks.datacommons_tools.cli.common import load_settings_from_args
from bblocks.datacommons_tools.gcp_utilities.pipeline import (
    upload_to_cloud_storage,
    run_data_load,
    redeploy_service,
)
from bblocks.datacommons_tools.gcp_utilities.settings import get_kg_settings, KGSettings

__all__ = ["add_parser", "run"]


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``pipeline`` subcommand."""
    parser = subparsers.add_parser(
        "pipeline", help="Run the full Knowledge Graph loading pipeline"
    )
    parser.add_argument(
        "--settings-file", type=Path, help="Path to the KG settings JSON file"
    )
    parser.add_argument(
        "--env-file", type=Path, help="Optional .env file containing KG settings"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Local directory to upload. Defaults to settings.LOCAL_PATH",
    )
    parser.add_argument(
        "--load-timeout",
        type=int,
        default=6000,
        help="Timeout for the data load job (default: %(default)s)",
    )
    parser.add_argument(
        "--deploy-timeout",
        type=int,
        default=600,
        help="Timeout for the service redeploy (default: %(default)s)",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Execute the ``pipeline`` command."""
    settings = load_settings_from_args(args)
    upload_to_cloud_storage(settings=settings, directory=args.directory)
    run_data_load(settings=settings, timeout=args.load_timeout)
    redeploy_service(settings=settings, timeout=args.deploy_timeout)
    return 0
