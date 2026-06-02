from app.rules.numeric_rules import PercentageCalculationRule
from app.schemas.parsed_content import ParsedDocument, ParsedParagraph
from app.tests.rule_test_utils import make_context


def test_percentage_calculation_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_numeric",
        paragraphs=[ParsedParagraph(text="3/20 subjects (20.0%) had TEAE.", paragraph_index=0)],
    )
    results = PercentageCalculationRule().run(make_context(parsed))
    assert results[0].severity == "High"
    assert "15.0%" in results[0].description
