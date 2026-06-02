from app.rules.reference_rules import MissingTableFigureReferenceRule
from app.schemas.parsed_content import ParsedDocument, ParsedParagraph, ParsedTableData
from app.tests.rule_test_utils import make_context


def test_missing_table_reference_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_ref",
        paragraphs=[ParsedParagraph(text="See Table 2 for details.", paragraph_index=0)],
        tables=[ParsedTableData(table_index=0, rows=[["A"]], markdown="", caption="Table 1. Existing")],
    )
    results = MissingTableFigureReferenceRule().run(make_context(parsed))
    assert results[0].rule_id == "REF-001"
