#!/usr/bin/env python
"""
Entrypoint script for running the reporting API to generate summary reports
from multiple verification case results.

This script wraps the Reporting.report_multiple_cases() function for use in
a Docker container.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

from constrain.api.reporting import Reporting


def main():
    parser = argparse.ArgumentParser(
        description='Generate summary reports from verification case results',
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
        """
    )
    
    parser.add_argument(
        'verification_json',
        help='Path to verification result JSON files. Use wildcards for multiple files (e.g., "/app/results/*_md.json")'
    )
    
    parser.add_argument(
        '--output',
        default='results.md',
        help='Name of the output summary report file (default: results.md)'
    )
    
    parser.add_argument(
        '--items',
        nargs='*',
        default=[],
        help='List of verification class names to include. If empty, all results are included'
    )
    
    parser.add_argument(
        '--format',
        default='markdown',
        choices=['markdown'],
        help='Output format (default: markdown). Currently only markdown is supported'
    )
    
    args = parser.parse_args()
    
    # Validate that the verification_json path exists
    # Note: glob patterns won't exist until expanded, so we check the directory
    verification_dir = os.path.dirname(args.verification_json)
    if verification_dir and not os.path.exists(verification_dir):
        print(f"Error: Directory does not exist: {verification_dir}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create Reporting instance
        print(f"Initializing reporting for: {args.verification_json}")
        print(f"Output file: {args.output}")
        if args.items:
            print(f"Filtering for items: {', '.join(args.items)}")
        else:
            print("Including all verification results")
        
        reporting = Reporting(
            verification_json=args.verification_json,
            result_md_name=args.output,
            report_format=args.format
        )
        
        # Generate report
        print("\nGenerating report...")
        reporting.report_multiple_cases(item_names=args.items)
        
        # Get the output path
        output_path = reporting.result_md_path
        
        print(f"\n✓ Report generated successfully!")
        print(f"  Summary report: {output_path}")
        print(f"  Individual case reports: {reporting.result_md_dir}/case-*.md")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error generating report: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
