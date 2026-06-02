from app.rules.heading_rules import HeadingNumberingGapRule
from app.schemas.parsed_content import ParsedDocument, ParsedHeading
from app.tests.rule_test_utils import make_context


def test_heading_numbering_gap_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_head",
        headings=[
            ParsedHeading(text="3.1 Study Design", paragraph_index=0, section_number="3.1", section_title="Study Design"),
            ParsedHeading(text="3.3 Dose Escalation", paragraph_index=1, section_number="3.3", section_title="Dose Escalation"),
        ],
    )
    results = HeadingNumberingGapRule().run(make_context(parsed))
    assert "3.2" in results[0].description
