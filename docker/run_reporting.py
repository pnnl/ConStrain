#!/usr/bin/env python
"""
Entrypoint script for running the reporting API to generate summary reports
from multiple verification case results.

This script wraps the Reporting.report_multiple_cases() function for use in
a Docker container.
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, "/app")

from constrain.api.reporting import Reporting


def main():
    parser = argparse.ArgumentParser(
        description="Generate summary reports from verification case results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Report all verification results in a directory
  python run_reporting.py "/app/results/*_md.json" --output results.md

  # Report specific verification classes
  python run_reporting.py "/app/results/*_md.json" \\
    --output results.md \\
    --items "G36FreezeProtectionStage1" "G36FreezeProtectionStage2"

  # Report with custom output directory
  python run_reporting.py "/app/results/*_md.json" \\
    --output summary.md \\
    --format markdown
        """,
    )

    parser.add_argument(
        "verification_json",
        help='Path to verification result JSON files. Use wildcards for multiple files (e.g., "/app/results/*_md.json")',
    )

    parser.add_argument(
        "--output",
        default="results.md",
        help="Name of the output summary report file (default: results.md)",
    )

    parser.add_argument(
        "--items",
        nargs="*",
        default=[],
        help="List of verification class names to include. If empty, all results are included",
    )

    parser.add_argument(
        "--format",
        default="markdown",
        choices=["markdown"],
        help="Output format (default: markdown). Currently only markdown is supported",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Configure logging with the specified level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s: %(message)s",
        force=True,  # Force reconfiguration even if logging was already configured
    )
    logger = logging.getLogger(__name__)

    # Validate that the verification_json path exists
    # Note: glob patterns won't exist until expanded, so we check the directory
    verification_dir = os.path.dirname(args.verification_json)
    if verification_dir and not os.path.exists(verification_dir):
        logger.error(f"Directory does not exist: {verification_dir}")
        sys.exit(1)

    try:
        # Create Reporting instance
        logger.info(f"Initializing reporting for: {args.verification_json}")
        logger.info(f"Output file: {args.output}")
        if args.items:
            logger.info(f"Filtering for items: {', '.join(args.items)}")
        else:
            logger.info("Including all verification results")

        reporting = Reporting(
            verification_json=args.verification_json,
            result_md_name=args.output,
            report_format=args.format,
        )

        # Generate report
        logger.info("Generating report...")
        reporting.report_multiple_cases(item_names=args.items)

        # Get the output path
        output_path = reporting.result_md_path

        logger.info("Report generated successfully!")
        logger.info(f"  Summary report: {output_path}")
        logger.info(f"  Individual case reports: {reporting.result_md_dir}/case-*.md")

        return 0

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
