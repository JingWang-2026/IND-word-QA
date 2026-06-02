from app.models.document import Document
from app.rules.base import RuleContext
from app.schemas.parsed_content import ParsedDocument


def make_context(parsed: ParsedDocument) -> RuleContext:
    document = Document(
        id=parsed.document_id,
        project_id="project_rule_tests",
        filename="rule-test.docx",
        stored_path="rule-test.docx",
        file_size=1,
        status="parsed",
    )
    return RuleContext(project_id=document.project_id, document=document, parsed_document=parsed, all_project_documents=[parsed])
