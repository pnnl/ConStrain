"""
Test the Streamlit Docker container and application.

This test verifies that:
1. The Streamlit Docker container can be built successfully
2. The Streamlit application starts without errors
3. The application can be accessed via HTTP
4. The container has proper volume and network configuration
"""

import subprocess
import time
import requests
import pytest


def test_streamlit_docker_build():
    """Test that the Streamlit Docker image builds successfully."""
    result = subprocess.run(
        [
            "docker",
            "build",
            "-t",
            "constrain-streamlit:test",
            "-f",
            "docker/Dockerfile.streamlit",
            ".",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"


def test_streamlit_container_starts():
    """Test that the Streamlit container starts successfully."""
    # Start the container
    start_result = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            "constrain-streamlit-test",
            "-p",
            "8502:8501",
            "-v",
            "streamlit-test-uploads:/app/uploads",
            "constrain-streamlit:test",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    try:
        assert (
            start_result.returncode == 0
        ), f"Container start failed: {start_result.stderr}"
        container_id = start_result.stdout.strip()

        # Wait for Streamlit to start
        max_retries = 30
        for i in range(max_retries):
            time.sleep(1)
            # Check if container is still running
            check_result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_id],
                capture_output=True,
                text=True,
            )
            if check_result.stdout.strip() != "true":
                # Container stopped, get logs
                logs = subprocess.run(
                    ["docker", "logs", container_id],
                    capture_output=True,
                    text=True,
                )
                pytest.fail(
                    f"Container stopped unexpectedly. Logs:\n{logs.stdout}\n{logs.stderr}"
                )

            # Try to connect to Streamlit
            try:
                response = requests.get("http://localhost:8502", timeout=2)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass

            if i == max_retries - 1:
                # Get container logs for debugging
                logs = subprocess.run(
                    ["docker", "logs", container_id],
                    capture_output=True,
                    text=True,
                )
                pytest.fail(
                    f"Streamlit did not start within {max_retries} seconds. Logs:\n{logs.stdout}\n{logs.stderr}"
                )

        # Verify Streamlit is accessible
        response = requests.get("http://localhost:8502", timeout=5)
        assert (
            response.status_code == 200
        ), f"Streamlit app not accessible: {response.status_code}"

        # Verify the response contains Streamlit content
        assert "streamlit" in response.text.lower() or "ConStrain" in response.text

    finally:
        # Clean up: stop and remove container
        subprocess.run(
            ["docker", "stop", "constrain-streamlit-test"],
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["docker", "rm", "constrain-streamlit-test"],
            capture_output=True,
            timeout=30,
        )
        # Clean up volume
        subprocess.run(
            ["docker", "volume", "rm", "streamlit-test-uploads"],
            capture_output=True,
            timeout=30,
        )


def test_streamlit_app_imports():
    """Test that the Streamlit app module can be imported without errors."""
    result = subprocess.run(
        [
            "python",
            "-c",
            "import sys; sys.path.insert(0, 'docker'); "
            "import streamlit_app; "
            "print('Import successful')",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "Import successful" in result.stdout


def test_streamlit_config_exists():
    """Test that the Streamlit config file exists and is valid."""
    import os

    config_path = "docker/.streamlit/config.toml"
    assert os.path.exists(config_path), f"Config file not found: {config_path}"

    # Try to parse the config file
    try:
        import tomli

        with open(config_path, "rb") as f:
            config = tomli.load(f)
        assert "theme" in config, "Theme section missing from config"
        assert config["theme"]["base"] == "light", "Theme base should be 'light'"
    except ImportError:
        # tomli not available, just check file exists and has content
        with open(config_path, "r") as f:
            content = f.read()
        assert len(content) > 0, "Config file is empty"
        assert 'base = "light"' in content, "Light theme not configured"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
