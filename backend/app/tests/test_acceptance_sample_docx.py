from pathlib import Path

from app.models.document import Document
from app.rules.base import RuleContext
from app.services.docx_parser import DocxParserService
from app.services.qa_engine import QAEngine
from app.tests.fixtures.generate_sample_docx import create_sample_bad_report, create_sample_clean_report


def _run_fixture(path: Path):
    document = Document(
        id=f"doc_{path.stem}",
        project_id="project_acceptance",
        filename=path.name,
        stored_path=str(path),
        file_size=path.stat().st_size,
        status="parsed",
    )
    parsed = DocxParserService().parse(document.id, str(path))
    return QAEngine().run_document_qa(
        RuleContext(project_id=document.project_id, document=document, parsed_document=parsed, all_project_documents=[parsed])
    )


def test_sample_bad_report_generates_expected_issues(tmp_path: Path) -> None:
    issues = _run_fixture(create_sample_bad_report(tmp_path / "sample_bad_report.docx"))
    rule_ids = {issue.rule_id for issue in issues}
    assert len(issues) >= 8
    assert {"TEXT-001", "NUM-001", "TABLE-001", "WORD-002", "WORD-003"}.issubset(rule_ids)


def test_sample_clean_report_generates_no_high_issues(tmp_path: Path) -> None:
    issues = _run_fixture(create_sample_clean_report(tmp_path / "sample_clean_report.docx"))
    assert not [issue for issue in issues if issue.severity == "High"]
