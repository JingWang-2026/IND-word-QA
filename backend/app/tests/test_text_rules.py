from app.rules.text_rules import DuplicateWordRule, RepeatedSpacesRule
from app.schemas.parsed_content import ParsedDocument, ParsedParagraph
from app.tests.rule_test_utils import make_context


def test_duplicate_word_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_text",
        paragraphs=[ParsedParagraph(text="The the dose escalation starts.", paragraph_index=0)],
    )
    results = DuplicateWordRule().run(make_context(parsed))
    assert results[0].rule_id == "TEXT-001"


def test_repeated_spaces_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_spaces",
        paragraphs=[ParsedParagraph(text="Dose  escalation starts.", paragraph_index=0)],
    )
    results = RepeatedSpacesRule().run(make_context(parsed))
    assert results[0].rule_id == "TEXT-002"
