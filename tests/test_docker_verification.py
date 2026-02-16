"""
Test for Docker verification image
Tests that the Docker image builds and verification cases run successfully
"""

import subprocess
import pytest
import os


@pytest.mark.skipif(
    os.environ.get("SKIP_DOCKER_TESTS") == "1",
    reason="Docker tests skipped (set SKIP_DOCKER_TESTS=1 to skip)",
)
class TestDockerVerification:
    """Test suite for Docker verification image"""

    def test_docker_image_builds(self):
        """Test that the Docker verification image builds successfully"""
        print("\n[BUILD] Building Docker verification image...")
        result = subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.verification",
                "-t",
                "constrain-verification:test",
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
                "docker/Dockerfile.verification",
                "-t",
                "constrain-verification:test",
                ".",
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            timeout=600,
        )

        # Run the container with --help
        result = subprocess.run(
            ["docker", "run", "--rm", "constrain-verification:test", "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + result.stderr

        # Check for help text
        assert "usage:" in output.lower() or "Run a single ConStrain verification case" in output, (
            f"Expected help text in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] Help command works correctly")

    def test_verification_case_runs_successfully(self):
        """Test that a verification case runs successfully with mounted example data"""
        print("\n[RUN] Running verification case with example data...")

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.verification",
                "-t",
                "constrain-verification:test",
                ".",
            ],
            cwd=project_root,
            capture_output=True,
            timeout=600,
        )

        # Run the container with mounted example verification case
        result = subprocess.run(
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
                "constrain-verification:test",
                "/app/workflows/G36_library_verification_cases.json",
                "--data",
                "/app/data/G36_Modelica_Jan.csv",
                "--lib-items",
                "/app/schema/library.json",
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for verification execution
        )

        output = result.stdout + result.stderr

        # Check for success message
        assert "✓ Verification completed successfully!" in output, (
            f"Expected '✓ Verification completed successfully!' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        # Verify verification ran
        assert "Running verification cases..." in output, (
            f"Expected 'Running verification cases...' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        # Verify configuration was successful
        assert "Configuring verification..." in output, (
            f"Expected 'Configuring verification...' in output, but it was not found.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] TEST PASSED: Verification case completed successfully!")
        print(f"Last few lines of output:\n{output[-500:]}")

    def test_verification_with_missing_file_fails_gracefully(self):
        """Test that verification fails gracefully when case file is missing"""
        print("\n[RUN] Testing error handling with missing case file...")

        # First ensure image is built
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "docker/Dockerfile.verification",
                "-t",
                "constrain-verification:test",
                ".",
            ],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            timeout=600,
        )

        # Run the container with non-existent file
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "constrain-verification:test",
                "/app/workflows/nonexistent.json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + result.stderr

        # Should fail with error message
        assert result.returncode != 0, "Expected non-zero return code for missing file"
        assert "not found" in output.lower() or "error" in output.lower(), (
            f"Expected error message about missing file.\n"
            f"Docker output:\n{output}"
        )

        print("[PASS] Error handling works correctly")
