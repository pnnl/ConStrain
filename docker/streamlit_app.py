"""
ConStrain Verification Streamlit Chatbot UI
A simple interface for uploading data files and running verification cases.

DEPRECATED: This legacy Streamlit UI is retained temporarily as reference/fallback
material while the API-first FastAPI UI reaches full feature parity. It is not
part of the supported docker-compose runtime.

Run this script directly on your host machine with:
    streamlit run streamlit_app.py

This avoids Docker-in-Docker complexity by running Streamlit natively.
"""

import streamlit as st
import os
import json
import subprocess
import tempfile
import shutil
import zipfile
from pathlib import Path

# Page configuration with light theme
st.set_page_config(
    page_title="ConStrain Verification Bot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
<style>
    /* Reduce font sizes for professional look */
    html, body, [class*="css"] {
        font-size: 14px;
    }
    
    h1 {
        font-size: 1.75rem;
        font-weight: 600;
    }
  
    h2 {
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    h3 {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .stButton > button {
        font-size: 14px;
    }
    
    .streamlit-expanderHeader {
        font-size: 14px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {
        "data_csv": None,
        "verification_json": None,
        "library_json": None,
    }
if "verification_running" not in st.session_state:
    st.session_state.verification_running = False
if "show_advanced" not in st.session_state:
    st.session_state.show_advanced = False

# Title
st.title("ConStrain Verification Bot")
st.markdown("---")

# Sidebar for file uploads
with st.sidebar:
    st.markdown("### Upload Files")

    st.markdown("**1. Data File (CSV)** *required*")
    data_file = st.file_uploader(
        "Upload your data CSV file",
        type=["csv"],
        key="data_uploader",
        help="Upload the CSV file containing your simulation or measured data",
    )

    st.markdown("**2. Verification Case (JSON)** *required*")
    verification_file = st.file_uploader(
        "Upload verification case JSON file",
        type=["json"],
        key="verification_uploader",
        help="Upload the JSON file defining your verification case",
    )

    st.markdown("**3. Library (JSON)** *optional*")
    library_file = st.file_uploader(
        "Upload ConStrain library JSON file (optional)",
        type=["json"],
        key="library_uploader",
        help="Upload the JSON file containing the ConStrain library definitions. If not provided, the default library will be used.",
    )

    st.markdown("---")

    # Show upload status
    st.markdown("**Upload Status**")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Data CSV:")
    with col2:
        if data_file:
            st.success("Ready")
            st.session_state.uploaded_files["data_csv"] = data_file
        else:
            st.error("Missing")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Verification JSON:")
    with col2:
        if verification_file:
            st.success("Ready")
            st.session_state.uploaded_files["verification_json"] = verification_file
        else:
            st.error("Missing")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Library JSON:")
    with col2:
        if library_file:
            st.success("Custom")
            st.session_state.uploaded_files["library_json"] = library_file
        else:
            st.info("Built-in")

# Main chat interface
st.markdown("### Verification Interface")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial bot greeting
if len(st.session_state.messages) == 0:
    greeting = """
**ConStrain Verification System**

Please upload the required files in the sidebar:
- **Data CSV**: Your simulation or measurement data
- **Verification Case JSON**: The verification case definition
- **Library JSON** (optional): Custom library items (defaults to built-in library if not provided)

Once files are uploaded, configure optional parameters and run the verification.
    """
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    with st.chat_message("assistant"):
        st.markdown(greeting)

# Check if required files are uploaded
all_files_uploaded = all(
    [
        st.session_state.uploaded_files["data_csv"],
        st.session_state.uploaded_files["verification_json"],
    ]
)

# Advanced options
if all_files_uploaded and not st.session_state.verification_running:
    st.markdown("---")
    st.markdown("### Configuration Options")

    # Advanced options toggle
    show_advanced = st.checkbox(
        "Show advanced options", value=st.session_state.show_advanced
    )
    st.session_state.show_advanced = show_advanced

    # Advanced options form
    if show_advanced:
        col1, col2 = st.columns(2)

        with col1:
            plot_option = st.selectbox(
                "Plot Option",
                options=["all-compact", "all-expand", "day-compact", "day-expand"],
                index=0,
                help="Type of plots to generate",
            )

            fig_width = st.number_input(
                "Figure Width", value=6.4, min_value=1.0, step=0.1
            )

            tolerance_file = st.file_uploader(
                "Custom Tolerances (JSON)",
                type=["json"],
                key="tolerance_uploader",
                help="Upload custom tolerance values (optional)",
            )

        with col2:
            log_level = st.selectbox(
                "Log Level",
                options=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
                index=0,
                help="Logging level for verification output",
            )

            fig_height = st.number_input(
                "Figure Height", value=4.8, min_value=1.0, step=0.1
            )
    else:
        # Use defaults when advanced options are hidden
        plot_option = "all-compact"
        tolerance_file = None
        fig_width = 6.4
        fig_height = 4.8
        log_level = "INFO"

    st.markdown("---")

# Run verification button
if all_files_uploaded and not st.session_state.verification_running:
    if st.button("Run Verification", type="primary", use_container_width=True):
        st.session_state.verification_running = True
        st.session_state.plot_option = plot_option
        st.session_state.tolerance_file = tolerance_file
        st.session_state.fig_size = f"{fig_width},{fig_height}"
        st.session_state.log_level = log_level
        st.rerun()

# Run the verification
if st.session_state.verification_running:
    with st.chat_message("assistant"):
        st.markdown("Starting verification process...")

        try:
            # Use /app/uploads inside container, which maps to ./docker/uploads on host
            import uuid
            import time
            import os

            # Create unique session directory
            session_id = str(uuid.uuid4())[:8]
            temp_path = Path(f"/app/uploads/session_{session_id}_{int(time.time())}")
            temp_path.mkdir(parents=True, exist_ok=True)

            # Save uploaded files
            data_path = temp_path / "data.csv"
            verification_path = temp_path / "verification_case.json"
            library_path = temp_path / "library.json"
            results_path = temp_path / "results"
            # Don't pre-create results directory - let the container create it
            # results_path.mkdir(exist_ok=True)

            with open(data_path, "wb") as f:
                f.write(st.session_state.uploaded_files["data_csv"].getvalue())

            with open(verification_path, "wb") as f:
                f.write(st.session_state.uploaded_files["verification_json"].getvalue())

            # Save library file if provided
            if st.session_state.uploaded_files["library_json"]:
                with open(library_path, "wb") as f:
                    f.write(st.session_state.uploaded_files["library_json"].getvalue())

            # Save tolerance file if provided
            tolerance_path = None
            if (
                hasattr(st.session_state, "tolerance_file")
                and st.session_state.tolerance_file
            ):
                tolerance_path = temp_path / "tolerances.json"
                with open(tolerance_path, "wb") as f:
                    f.write(st.session_state.tolerance_file.getvalue())

            st.markdown(f"Files saved to shared directory: `{temp_path}`")

            # Build docker command with required and optional parameters
            docker_cmd = [
                "docker",
                "run",
                "--rm",
                "--volumes-from",
                "constrain-streamlit",
                "--network",
                "docker_constrain-network",
                "constrain-verification:latest",
                str(verification_path),
                "--data",
                str(data_path),
                "--output",
                str(results_path),
            ]

            # Add library path if provided, otherwise use default which is already in the container
            if st.session_state.uploaded_files["library_json"]:
                docker_cmd.extend(["--lib-items", str(library_path)])
            else:
                # Use the default library path inside the container
                docker_cmd.extend(["--lib-items", "/app/constrain/schema/library.json"])

            # Add optional parameters
            if hasattr(st.session_state, "plot_option"):
                docker_cmd.extend(["--plot-option", st.session_state.plot_option])

            if hasattr(st.session_state, "fig_size"):
                docker_cmd.extend(["--fig-size", st.session_state.fig_size])

            if tolerance_path:
                docker_cmd.extend(["--tolerances", str(tolerance_path)])

            # Add log level
            if hasattr(st.session_state, "log_level"):
                docker_cmd.extend(["--log-level", st.session_state.log_level])

            st.markdown("Running Docker container...")
            with st.expander("Docker Command", expanded=False):
                st.code(" ".join(docker_cmd), language="bash")

            # Run the verification
            with st.spinner("Running verification... This may take a few minutes."):
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                )

            # Display results
            if result.returncode == 0:
                st.success("Verification completed successfully!")

                # Show output (both stdout and stderr for complete logs)
                with st.expander("Verification Output", expanded=False):
                    if result.stdout:
                        st.markdown("**Standard Output:**")
                        st.code(result.stdout, language="text")
                    if result.stderr:
                        st.markdown("**Logs:**")
                        st.code(result.stderr, language="text")

                # Run reporting to generate summary
                st.markdown("Generating summary report...")
                reporting_cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "--volumes-from",
                    "constrain-streamlit",
                    "--network",
                    "docker_constrain-network",
                    "constrain-reporting:latest",
                    f"{results_path}/*_md.json",
                    "--output",
                    "verification_summary.md",
                ]

                with st.expander("Reporting Command", expanded=False):
                    st.code(" ".join(reporting_cmd), language="bash")

                with st.spinner("Generating summary report..."):
                    report_result = subprocess.run(
                        reporting_cmd,
                        capture_output=True,
                        text=True,
                        timeout=120,  # 2 minute timeout for reporting
                    )

                report_generated = report_result.returncode == 0

                if report_generated:
                    st.success("Summary report generated!")
                    with st.expander("Reporting Output", expanded=False):
                        if report_result.stdout:
                            st.markdown("**Standard Output:**")
                            st.code(report_result.stdout, language="text")
                        if report_result.stderr:
                            st.markdown("**Logs:**")
                            st.code(report_result.stderr, language="text")

                    # Render the markdown report
                    summary_report_path = results_path / "verification_summary.md"
                    if summary_report_path.exists():
                        st.markdown("---")
                        st.markdown("### Verification Summary Report")
                        with open(summary_report_path, "r") as f:
                            report_content = f.read()

                        # Fix relative markdown links to work in Streamlit
                        # Convert links like [123](./case-123.md) to just display the text
                        import re

                        # Replace markdown links with just the link text
                        report_content = re.sub(
                            r"\[([^\]]+)\]\(\./case-\d+\.md\)", r"\1", report_content
                        )

                        st.markdown(report_content, unsafe_allow_html=True)
                else:
                    st.warning(
                        "Report generation had issues (verification still successful)"
                    )
                    with st.expander("Reporting Errors", expanded=False):
                        st.code(report_result.stderr, language="text")

                # Create zip file with all results
                result_files = [f for f in results_path.rglob("*") if f.is_file()]
                if result_files:
                    st.markdown("---")
                    st.markdown("### Download Results")

                    # Create zip file
                    zip_path = temp_path / "verification_results.zip"
                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for file_path in result_files:
                            # Add file to zip with relative path
                            arcname = file_path.relative_to(results_path)
                            zipf.write(file_path, arcname)

                    # Provide download button for zip file
                    with open(zip_path, "rb") as f:
                        st.download_button(
                            label=f"Download All Results (ZIP - {len(result_files)} files)",
                            data=f.read(),
                            file_name="verification_results.zip",
                            mime="application/zip",
                            type="primary",
                        )

                    # Show file list
                    with st.expander(
                        f"View file list ({len(result_files)} files)", expanded=False
                    ):
                        # Group files by directory
                        files_by_dir = {}
                        for file_path in sorted(result_files):
                            rel_path = file_path.relative_to(results_path)
                            dir_name = (
                                str(rel_path.parent)
                                if rel_path.parent != Path(".")
                                else "Root"
                            )
                            if dir_name not in files_by_dir:
                                files_by_dir[dir_name] = []
                            files_by_dir[dir_name].append(rel_path)

                        # Display files grouped by directory
                        for dir_name, files in files_by_dir.items():
                            if dir_name != "Root":
                                st.markdown(f"**{dir_name}/**")
                            for rel_path in files:
                                st.markdown(f"- `{rel_path}`")

                message = "Verification completed successfully! Download the results ZIP file above."
            else:
                st.error("Verification failed!")
                with st.expander("Error Details", expanded=True):
                    st.code(result.stderr, language="text")
                message = f"Verification failed with return code {result.returncode}. Check the error output above."

        except subprocess.TimeoutExpired:
            st.error("Verification timed out after 10 minutes")
            message = (
                "Verification timed out. Please check your input files and try again."
            )
        except Exception as e:
            st.error(f"Error: {str(e)}")
            message = f"An error occurred: {str(e)}"

        # Add to chat history
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.verification_running = False

# Chat input (disabled during verification)
if prompt := st.chat_input(
    "Ask me anything about the verification process...",
    disabled=st.session_state.verification_running,
):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        if not all_files_uploaded:
            response = "Please upload the required files (Data CSV and Verification JSON) in the sidebar before running the verification. The Library JSON file is optional."
        elif "help" in prompt.lower():
            response = """
            Here's how to use this verification tool:
            
            1. **Upload Files**: Use the sidebar to upload your three required files
            2. **Run Verification**: Click the "Run Verification" button
            3. **View Results**: Check the output and download result files
            
            The verification process uses Docker to run ConStrain in an isolated environment.
            """
        elif "what" in prompt.lower() and "constrain" in prompt.lower():
            response = """
            ConStrain is a building HVAC system verification tool that:
            - Validates control sequences against standards (ASHRAE 90.1, Guideline 36, etc.)
            - Checks simulation data or measured data for compliance
            - Generates detailed reports on verification results
            """
        else:
            response = f"I received your message: '{prompt}'. For now, I can help you run verifications. Please upload the required files and click 'Run Verification' to proceed."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>ConStrain Verification Bot | Built with Streamlit | Powered by Docker</small>
    </div>
    """,
    unsafe_allow_html=True,
)
