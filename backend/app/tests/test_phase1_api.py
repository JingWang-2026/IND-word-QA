from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.database import engine, init_db
from app.main import app
from app.models.issue import QAIssue
from app.models.project import Project


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_project_crud_and_docx_upload() -> None:
    init_db()
    project_response = client.post(
        "/api/projects",
        json={"name": "Phase 1 API Test", "description": "basic CRUD"},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    list_response = client.get("/api/projects")
    assert list_response.status_code == 200
    assert any(project["id"] == project_id for project in list_response.json())

    bad_upload = client.post(
        f"/api/projects/{project_id}/documents",
        files={"file": ("bad.doc", BytesIO(b"not a docx"), "application/msword")},
    )
    assert bad_upload.status_code == 400

    good_upload = client.post(
        f"/api/projects/{project_id}/documents",
        files={
            "file": (
                "report.docx",
                BytesIO(b"PK\x03\x04fake-docx-for-phase-1-upload"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert good_upload.status_code == 201
    assert good_upload.json()["status"] == "uploaded"

    docs_response = client.get(f"/api/projects/{project_id}/documents")
    assert docs_response.status_code == 200
    assert len(docs_response.json()) == 1


def test_issue_list_requires_existing_project() -> None:
    response = client.get("/api/projects/unknown/issues")
    assert response.status_code == 404


def test_issue_status_update() -> None:
    init_db()
    project_id = f"project_{uuid4().hex}"
    issue_id = f"issue_{uuid4().hex}"
    with Session(engine) as session:
        project = Project(id=project_id, name="Issue Patch Test")
        issue = QAIssue(
            id=issue_id,
            project_id=project_id,
            severity="Low",
            category="Text",
            rule_id="TEXT-001",
            title="Duplicated word",
            description="Repeated word found.",
            source_text="The the dose",
            suggestion="Remove one duplicated word.",
        )
        session.add(project)
        session.add(issue)
        session.commit()

    response = client.patch(
        f"/api/issues/{issue_id}",
        json={"status": "Confirmed", "reviewer_comment": "Confirmed by reviewer."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Confirmed"
    assert data["reviewer_comment"] == "Confirmed by reviewer."
