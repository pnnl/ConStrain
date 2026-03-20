import io
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from constrain.app.ai_workflow_server import app


client = TestClient(app)


def _create_artifacts(tmp_path: Path) -> Path:
    output_dir = tmp_path / "results"
    nested_dir = output_dir / "nested"
    nested_dir.mkdir(parents=True)

    (output_dir / "summary.md").write_text("# Summary\n", encoding="utf-8")
    (nested_dir / "case-1.md").write_text("case content\n", encoding="utf-8")
    return output_dir


def test_list_artifacts_returns_relative_paths(tmp_path: Path) -> None:
    output_dir = _create_artifacts(tmp_path)

    response = client.get(
        "/ai/artifacts/list",
        params={"output_dir": str(output_dir), "recursive": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2

    relative_paths = {item["relative_path"] for item in payload["artifacts"]}
    assert relative_paths == {"summary.md", "nested/case-1.md"}


def test_download_artifact_file_success(tmp_path: Path) -> None:
    output_dir = _create_artifacts(tmp_path)

    response = client.get(
        "/ai/artifacts/download",
        params={"output_dir": str(output_dir), "relative_path": "summary.md"},
    )

    assert response.status_code == 200
    assert response.content == b"# Summary\n"


def test_download_artifact_blocks_path_traversal(tmp_path: Path) -> None:
    output_dir = _create_artifacts(tmp_path)

    response = client.get(
        "/ai/artifacts/download",
        params={"output_dir": str(output_dir), "relative_path": "../outside.txt"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid artifact path."


def test_download_zip_contains_all_artifacts(tmp_path: Path) -> None:
    output_dir = _create_artifacts(tmp_path)

    response = client.get(
        "/ai/artifacts/download-zip",
        params={"output_dir": str(output_dir)},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/zip")

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
        names = set(zf.namelist())

    assert names == {"summary.md", "nested/case-1.md"}
