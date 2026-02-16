"""
Test for Docker reporting image
Tests that the Docker image builds and reporting runs successfully
"""

import subprocess
import pytest
import os


@pytest.mark.skipif(
    os.environ.get("SKIP_DOCKER_TESTS") == "1",
    reason="Docker tests skipped (set SKIP_DOCKER_TESTS=1 to skip)",
)
class TestDockerReporting:
    """Test suite for Docker reporting image"""

    def test_docker_image_builds(self):
        """Test that the Docker reporting image builds successfully"""
        print("\n[BUILD] Building Docker reporting image...")
        result = subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.reporting",
                "-t",
                "constrain-reporting:test",
                ".",
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for building
        )

        assert result.returncode == 0, f"Docker build failed:\n{result.stderr}"
        print("[SUCCESS] Docker image built successfully")

    def test_help_command_works(self):
        """Test that the help command works"""
        print("\n[RUN] Testing help command...")

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.reporting",
                "-t",
                "constrain-reporting:test",
                ".",
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            timeout=600,
        )

        # Run the container with --help
        result = subprocess.run(
            ["docker", "run", "--rm", "constrain-reporting:test", "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + result.stderr

        # Check for help text
        assert (
            "usage:" in output.lower()
            or "Generate summary reports from verification case results" in output
        ), (
            f"Expected help text in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] Help command works correctly")

    def test_reporting_runs_successfully(self):
        """Test that reporting runs successfully with mounted example results"""
        print("\n[RUN] Running reporting with example verification results...")

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.reporting",
                "-t",
                "constrain-reporting:test",
                ".",
            ],
            cwd=project_root,
            capture_output=True,
            timeout=600,
        )

        # Create a temporary directory for results
        temp_results_dir = os.path.join(project_root, "docker/examples_results_test")
        os.makedirs(temp_results_dir, exist_ok=True)

        # First, run a verification to generate results
        print("[SETUP] Running verification to generate test data...")
        verification_result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{project_root}/docker/examples/verification_cases:/app/workflows",
                "-v",
                f"{project_root}/docker/examples/data:/app/data",
                "-v",
                f"{project_root}/docker/examples/schema:/app/schema",
                "-v",
                f"{temp_results_dir}:/app/results",
                "constrain-verification:test",
                "/app/workflows/G36_library_verification_cases.json",
                "--data",
                "/app/data/G36_Modelica_Jan.csv",
                "--lib-items",
                "/app/schema/library.json",
                "--output",
                "/app/results",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if verification_result.returncode != 0:
            print(
                f"[WARNING] Verification setup failed, using any existing results:\n{verification_result.stderr}"
            )

        # Run the reporting container
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{temp_results_dir}:/app/results",
                "constrain-reporting:test",
                "/app/results/*_md.json",
                "--output",
                "test_summary.md",
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for reporting execution
        )

        output = result.stdout + result.stderr

        # Check for success message
        assert "Report generated successfully!" in output, (
            f"Expected 'Report generated successfully!' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        # Verify report initialization
        assert "Initializing reporting for:" in output, (
            f"Expected 'Initializing reporting for:' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        # Verify report generation
        assert "Generating report..." in output, (
            f"Expected 'Generating report...' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] TEST PASSED: Reporting completed successfully!")
        print(f"Last few lines of output:\n{output[-500:]}")

    def test_reporting_with_missing_files_fails_gracefully(self):
        """Test that reporting fails gracefully when result files are missing"""
        print("\n[RUN] Testing error handling with missing result files...")

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.reporting",
                "-t",
                "constrain-reporting:test",
                ".",
            ],
            cwd=project_root,
            capture_output=True,
            timeout=600,
        )

        # Run the container with non-existent directory
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "constrain-reporting:test",
                "/app/nonexistent/*_md.json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + result.stderr

        # Should fail with error message
        assert result.returncode != 0, "Expected non-zero return code for missing files"
        assert "not exist" in output.lower() or "error" in output.lower(), (
            f"Expected error message about missing files.\n" f"Docker output:\n{output}"
        )

        print("[PASS] Error handling works correctly")

    def test_reporting_with_log_level_option(self):
        """Test that the --log-level option works correctly"""
        print("\n[RUN] Testing --log-level option...")

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.reporting",
                "-t",
                "constrain-reporting:test",
                ".",
            ],
            cwd=project_root,
            capture_output=True,
            timeout=600,
        )

        # Create a temporary directory for results
        temp_results_dir = os.path.join(project_root, "docker/examples_results_test")
        os.makedirs(temp_results_dir, exist_ok=True)

        # Run with DEBUG log level
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{temp_results_dir}:/app/results",
                "constrain-reporting:test",
                "/app/results/*_md.json",
                "--output",
                "test_summary.md",
                "--log-level",
                "DEBUG",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        output = result.stdout + result.stderr

        # With DEBUG level, we should see log messages
        # Note: We're just checking that --log-level is accepted without error
        assert "--log-level" not in output or "unrecognized arguments" not in output, (
            f"The --log-level option should be recognized.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] --log-level option works correctly")
