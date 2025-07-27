import argparse
from pathlib import Path
from typing import Optional, List

from ..core.classes import CLIConfig
from ..core.mutators import list_mutators


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    p = argparse.ArgumentParser(
        prog="quill",
        description="Adversarial-prompt fuzzer for LLMs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Subcommands
    subparsers = p.add_subparsers(dest="command", help="Commands")

    # Fuzzing command (default)
    fuzz_parser = subparsers.add_parser(
        "fuzz",
        help="Run fuzzing tests on an LLM",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    fuzz_parser.add_argument(
        "-c",
        "--corpus",
        type=Path,
        help="Path to corpus directory or file with corpus prompts",
    )
    fuzz_parser.add_argument(
        "-o",
        "--outdir",
        type=Path,
        default=Path("runs/latest"),
        help="Where to write prompts & responses",
    )
    fuzz_parser.add_argument(
        "-n",
        "--max-prompts",
        type=int,
        default=1000,
        help="Maximum number of prompts to process (when corpus specified, uses only available corpus prompts)",
    )
    fuzz_parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature for the target model",
    )
    fuzz_parser.add_argument(
        "-x",
        "--mutations",
        nargs="+",
        default=["typo"],
        help=f"Mutation strategies to apply. Available: {list_mutators()}",
    )
    fuzz_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Debug-level logging"
    )
    fuzz_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    # Async options
    fuzz_parser.add_argument(
        "--async",
        action="store_true",
        help="Use async processing for improved performance"
    )
    fuzz_parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of requests to process in each batch (async mode)"
    )
    fuzz_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent requests (async mode)"
    )

    # Mode subcommands for fuzzing
    fuzz_subparsers = fuzz_parser.add_subparsers(
        dest="mode", required=True, help="Mode of operation"
    )
    http_parser = fuzz_subparsers.add_parser("http", help="Use HTTP client mode")
    http_parser.add_argument("--url", required=True, help="HTTP endpoint URL")
    ollama_parser = fuzz_subparsers.add_parser("ollama", help="Use Ollama client mode")
    ollama_parser.add_argument(
        "--model",
        required=True,
        help="Ollama model name or endpoint alias (e.g. gemma3:27b)",
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate HTML report from fuzzing results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    report_parser.add_argument(
        "results_dir", type=Path, help="Directory containing fuzzing results"
    )
    report_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to save the HTML report to (defaults to results_dir/report.html)",
    )
    report_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Debug-level logging"
    )

    # Clean command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove output files from previous runs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    clean_parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path("runs/latest"),
        help="Directory containing fuzzing results to clean",
    )
    clean_parser.add_argument(
        "--all",
        action="store_true",
        help="Clean all runs directories instead of just the latest",
    )
    clean_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Debug-level logging"
    )
    clean_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution)",
    )

    return p


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Handle default command
    if not hasattr(args, "command") or args.command is None:
        args.command = "fuzz"

    return args


def parse_fuzz_args(args: argparse.Namespace) -> CLIConfig:
    """Convert parsed arguments to a CLIConfig object for fuzzing."""
    # Convert namespace to dictionary and filter out command
    config_dict = {k: v for k, v in vars(args).items() if k != "command"}
    return CLIConfig(**config_dict)
