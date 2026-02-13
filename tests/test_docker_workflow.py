"""
Test for Docker workflow image
Tests that the Docker image builds and the default workflow runs successfully
"""

import subprocess
import pytest
import os


@pytest.mark.skipif(
    os.environ.get("SKIP_DOCKER_TESTS") == "1",
    reason="Docker tests skipped (set SKIP_DOCKER_TESTS=1 to skip)",
)
class TestDockerWorkflow:
    """Test suite for Docker workflow image"""

    def test_docker_image_builds(self):
        """Test that the Docker workflow image builds successfully"""
        print("\n[BUILD] Building Docker workflow image...")
        result = subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.workflow",
                "-t",
                "constrain:test",
                ".",
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for building
        )

        assert result.returncode == 0, f"Docker build failed:\n{result.stderr}"
        print("[SUCCESS] Docker image built successfully")

    def test_default_workflow_runs_successfully(self):
        """Test that the default G36 demo workflow completes successfully"""
        print("\n[RUN] Running default G36 demo workflow...")

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.workflow",
                "-t",
                "constrain:test",
                ".",
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            timeout=600,
        )

        # Run the container with default workflow
        result = subprocess.run(
            ["docker", "run", "--rm", "constrain:test"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for workflow execution
        )

        output = result.stdout + result.stderr

        # Check for success message
        assert "Workflow completed successfully!" in output, (
            f"Expected 'Workflow completed successfully!' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        # Verify workflow executed at least the core states (more flexible check)
        assert "Running state 7: [run verification]" in output, (
            f"Expected workflow to reach verification state, but it did not.\n"
            f"Docker output:\n{output}"
        )

        # Verify workflow completed without fatal errors
        assert "Workflow done at" in output, (
            f"Expected workflow to complete, but it did not.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] TEST PASSED: Default workflow completed successfully!")
        print(f"Last few lines of output:\n{output[-500:]}")
