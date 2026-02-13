#!/usr/bin/env python
"""
Entrypoint script for running ConStrain workflows in Docker.
Accepts a workflow JSON file path as a command-line argument.
"""
import sys
import os
from constrain.api import Workflow


def main():
    # Default to demo workflow if no argument provided
    default_workflow = "./constrain/demo/G36_demo/G36_demo_workflow.json"

    if len(sys.argv) > 1:
        workflow_path = sys.argv[1]
        is_default_workflow = False
    else:
        workflow_path = default_workflow
        is_default_workflow = True
        print(f"No workflow specified, using default: {workflow_path}")

    # Check if file exists
    if not os.path.exists(workflow_path):
        print(f"Error: Workflow file not found: {workflow_path}")
        sys.exit(1)

    print(f"Loading workflow from: {workflow_path}")

    # Only change working directory for the default demo workflow
    # This ensures relative paths in the demo workflow work correctly
    if is_default_workflow:
        constrain_root = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "constrain"
        )
        if os.path.exists(constrain_root):
            print(f"Changing working directory to: {constrain_root}")
            os.chdir(constrain_root)
            # Adjust workflow path to be relative to new working directory
            workflow_path = os.path.relpath(
                os.path.abspath(os.path.join("/app", workflow_path)), constrain_root
            )
            print(f"Adjusted workflow path: {workflow_path}")

    # Load and run the workflow
    try:
        workflow = Workflow(workflow=workflow_path)
        workflow.run_workflow(verbose=True)
        print("\nWorkflow completed successfully!")
    except Exception as e:
        print(f"\nError running workflow: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
