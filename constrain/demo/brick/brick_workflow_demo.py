# %% [markdown]
# # Brick Demo Workflow
#
# The goal of this demo is to showcase how the ConStrain Brick API can be used to:
# 1. Load Brick schema and instance data
# 2. Query verification case datapoints from Brick models
# 3. Run verification workflows with Brick-generated cases
# 4. Generate comprehensive reports and visualizations
#
# This demo leverages the ConStrain Brick compliance API to conduct building system verification analysis using semantic building models.
#
# ## Key Features:
# - **BrickCompliance**: Loads and queries Brick schema and instance files
# - **Workflow Engine**: Executes verification workflows defined in JSON configuration
# - **Zone Temperature Control**: Demonstrates verification of HVAC zone temperature setpoint deadband requirements
# - **Automated Reporting**: Generates markdown reports and JSON outputs
#
# ## Prerequisites:
# - The project uses `poetry` to manage its dependencies
# - Install dependencies by running `poetry install` in the root folder
# - Ensure all required Brick resource files are present in `resources/brick/`

# %% Imports and Setup
# Load dependencies and configure paths
import sys, warnings, os

try:
    # works in scripts
    base_path = os.path.dirname(__file__)
except NameError:
    # fallback for notebooks
    base_path = os.getcwd()

# Insert the root directory at the beginning of sys.path to prioritize local constrain package
sys.path.insert(0, os.path.join(base_path, "..", "..", ".."))

from constrain.api import Workflow

# Suppress warnings for cleaner output
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=ResourceWarning)

# %% [markdown]
# ## Workflow Configuration
#
# The workflow is defined in `brick_workflow.json` and includes the following key steps:
#
# 1. **BrickCompliance Instantiation**: Load Brick schema and instance files
# 2. **Datapoint Query**: Query verification case datapoints for zone temperature control
# 3. **Verification Case Setup**: Create and configure verification cases
# 4. **Data Processing**: Load and process building simulation timeseries data
# 5. **Verification Execution**: Run zone temperature control verification
# 6. **Report Generation**: Create markdown and JSON reports with visualizations
#
# ### Expected Workflow Outputs:
# - `data/query_result.json`: Brick query results
# - `data/1_md.json`, `data/2_md.json`: Individual case verification results
# - `data/case-1.md`, `data/case-2.md`: Individual case markdown reports
# - `data/report_summary.md`: Summary report with verification results table
# - `data/VerificationCase1/`, `data/VerificationCase2/`: Visualization plots

# %% Run Workflow
# Execute the complete Brick verification workflow
print("Starting Brick Demo Workflow...")
workflow = Workflow(workflow="./brick_workflow.json")
workflow.run_workflow(verbose=True)
print("Workflow completed successfully!")
