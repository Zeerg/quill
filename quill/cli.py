import argparse
import sys
import random
import logging
import os
from pathlib import Path
from typing import Optional, List

from .core.fuzzer import Fuzzer
from .core.async_fuzzer import AsyncFuzzer
from .utils.args import parse_args, parse_fuzz_args
from .utils.logging import get_logger
from .utils.report import generate_report
from .utils.clean import clean_directory, clean_all_runs


def run_fuzzer(args: argparse.Namespace, log: logging.Logger) -> None:
    """Run the fuzzer with the given arguments."""
    cfg = parse_fuzz_args(args)

    # Check if async mode is requested
    use_async = getattr(args, 'async', False)
    
    if use_async:
        log.info("Quill async fuzzing starting with %s", cfg)
    else:
        log.info("Quill fuzzing starting with %s", cfg)

    # Set random seed if provided
    if cfg.seed is not None:
        log.info(f"Setting random seed to {cfg.seed}")
        random.seed(cfg.seed)

    # Create appropriate fuzzer instance
    if use_async:
        fuzzer = AsyncFuzzer(
            mode=cfg.mode,
            model_id=cfg.model,
            url=cfg.url,
            output_dir=cfg.outdir,
            max_prompts=cfg.max_prompts,
            temperature=cfg.temperature,
            mutators=cfg.mutations,
            verbose=cfg.verbose,
            corpus_path=cfg.corpus,
            batch_size=getattr(args, 'batch_size', 10),
            max_concurrent=getattr(args, 'max_concurrent', 5),
        )
    else:
        fuzzer = Fuzzer(
            mode=cfg.mode,
            model_id=cfg.model,
            url=cfg.url,
            output_dir=cfg.outdir,
            max_prompts=cfg.max_prompts,
            temperature=cfg.temperature,
            mutators=cfg.mutations,
            verbose=cfg.verbose,
            corpus_path=cfg.corpus,
        )

    stats = fuzzer.run()

    # Only compute and display metrics if we have processed at least one prompt
    if stats.total > 0:
        stats.compute_metrics()

        log.info(
            "Completed %d prompts; %d anomalies detected (%.2f%%)",
            stats.total,
            stats.anomalies,
            stats.success_rate * 100,
        )

        if stats.anomalies > 0:
            log.info("Check the output directory for detailed anomaly reports")
    else:
        log.error("No prompts were processed. Check the logs for errors.")

    log.info(f"Results saved to {cfg.outdir}")


def generate_html_report(args: argparse.Namespace, log: logging.Logger) -> None:
    """Generate an HTML report from fuzzing results."""
    log.info(f"Generating HTML report from {args.results_dir}")

    # Generate the report
    report_path = generate_report(args.results_dir, args.output)

    log.info(f"Report generated successfully: {report_path}")
    log.info(f"Open it in your browser to view the results")


def clean_results(args: argparse.Namespace, log: logging.Logger) -> None:
    """Clean output files from previous runs."""
    directory = args.directory

    if args.all:
        # Clean all run directories
        runs_dir = Path("runs")
        if not runs_dir.exists():
            log.error(f"Runs directory {runs_dir} does not exist!")
            return

        if not args.confirm:
            confirm = input(
                f"Are you sure you want to delete all files in ALL run directories? [y/N] "
            )
            if confirm.lower() not in ["y", "yes"]:
                log.info("Operation cancelled.")
                return

        log.info(f"Cleaning all runs directories...")
        count, files = clean_all_runs(runs_dir)

        if count > 0:
            log.info(f"Removed {count} files from all run directories")
            if args.verbose:
                for file in files:
                    log.debug(f"Removed: {file}")
        else:
            log.info("No files to remove")
    else:
        # Clean single directory
        if not directory.exists():
            log.error(f"Directory {directory} does not exist!")
            return

        if not args.confirm:
            confirm = input(
                f"Are you sure you want to delete all files in {directory}? [y/N] "
            )
            if confirm.lower() not in ["y", "yes"]:
                log.info("Operation cancelled.")
                return

        log.info(f"🧹 Cleaning directory: {directory}")
        count, files = clean_directory(directory)

        if count > 0:
            log.info(f"Removed {count} files from {directory}")
            if args.verbose:
                for file in files:
                    log.debug(f"Removed: {file}")
        else:
            log.info("No files to remove")


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI."""
    args = parse_args(argv)

    # Set up logging
    if args.verbose:
        log = get_logger(__name__, debug=True)
    else:
        log = get_logger(__name__)

    # Handle commands
    if args.command == "fuzz":
        run_fuzzer(args, log)
    elif args.command == "report":
        generate_html_report(args, log)
    elif args.command == "clean":
        clean_results(args, log)
    else:
        log.error(f"Unknown command: {args.command}")
        sys.exit(1)
