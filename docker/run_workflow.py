#!/usr/bin/env python
"""
Entrypoint script for running ConStrain workflows in Docker.
Accepts a workflow JSON file path as a command-line argument.
"""
import sys
import os
import logging
import argparse
from constrain.api import Workflow


def main():
    parser = argparse.ArgumentParser(
        description="Run a ConStrain workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a custom workflow
  python run_workflow.py /app/workflows/my_workflow.json
  
  # Run with debug logging
  python run_workflow.py /app/workflows/my_workflow.json --log-level DEBUG
  
  # Run default demo workflow
  python run_workflow.py
        """,
    )

    parser.add_argument(
        "workflow_path",
        nargs="?",
        default="./constrain/demo/G36_demo/G36_demo_workflow.json",
        help="Path to the workflow JSON file (default: demo workflow)",
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

    # Default to demo workflow if no argument provided
    default_workflow = "./constrain/demo/G36_demo/G36_demo_workflow.json"
    workflow_path = args.workflow_path
    is_default_workflow = workflow_path == default_workflow

    if is_default_workflow:
        logger.info(f"No workflow specified, using default: {workflow_path}")

    # Check if file exists
    if not os.path.exists(workflow_path):
        logger.error(f"Workflow file not found: {workflow_path}")
        sys.exit(1)

    logger.info(f"Loading workflow from: {workflow_path}")

    # Only change working directory for the default demo workflow
    # This ensures relative paths in the demo workflow work correctly
    if is_default_workflow:
        constrain_root = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "constrain"
        )
        if os.path.exists(constrain_root):
            logger.info(f"Changing working directory to: {constrain_root}")
            os.chdir(constrain_root)
            # Adjust workflow path to be relative to new working directory
            workflow_path = os.path.relpath(
                os.path.abspath(os.path.join("/app", workflow_path)), constrain_root
            )
            logger.info(f"Adjusted workflow path: {workflow_path}")

    # Load and run the workflow
    try:
        workflow = Workflow(workflow=workflow_path)
        workflow.run_workflow(verbose=True)
        logger.info("Workflow completed successfully!")
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
