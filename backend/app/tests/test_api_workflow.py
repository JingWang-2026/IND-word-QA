from pathlib import Path

from fastapi.testclient import TestClient

from app.core.database import init_db
from app.main import app
from app.tests.fixtures.generate_sample_docx import create_sample_bad_report

client = TestClient(app)


def test_upload_parse_qa_export_workflow(tmp_path: Path) -> None:
    init_db()
    sample_path = create_sample_bad_report(tmp_path / "workflow_bad.docx")
    project_response = client.post("/api/projects", json={"name": "Workflow Test"})
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    with sample_path.open("rb") as file:
        upload_response = client.post(
            f"/api/projects/{project_id}/documents",
            files={
                "file": (
                    "workflow_bad.docx",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]

    parse_response = client.post(f"/api/documents/{document_id}/parse")
    assert parse_response.status_code == 200
    assert parse_response.json()["tracked_change_count"] == 1

    qa_response = client.post(f"/api/documents/{document_id}/qa/run")
    assert qa_response.status_code == 200
    assert qa_response.json()["issue_count"] >= 8

    issues_response = client.get(f"/api/projects/{project_id}/issues?severity=High")
    assert issues_response.status_code == 200
    assert len(issues_response.json()) >= 3

    export_response = client.get(f"/api/projects/{project_id}/export/issues.xlsx")
    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
