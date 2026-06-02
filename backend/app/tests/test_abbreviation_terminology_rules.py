from app.rules.abbreviation_rules import AbbreviationFirstDefinitionRule, AbbreviationMultipleDefinitionsRule
from app.rules.terminology_rules import SimpleTerminologyInconsistencyRule
from app.schemas.parsed_content import ParsedDocument, ParsedParagraph
from app.tests.rule_test_utils import make_context


def test_abbreviation_first_definition_rule() -> None:
    parsed = ParsedDocument(document_id="doc_abbr1", paragraphs=[ParsedParagraph(text="AE was monitored.", paragraph_index=0)])
    results = AbbreviationFirstDefinitionRule().run(make_context(parsed))
    assert results[0].rule_id == "ABBR-001"


def test_abbreviation_multiple_definitions_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_abbr2",
        paragraphs=[
            ParsedParagraph(text="dose-limiting toxicity (DLT) was recorded.", paragraph_index=0),
            ParsedParagraph(text="dose level testing (DLT) was recorded.", paragraph_index=1),
        ],
    )
    results = AbbreviationMultipleDefinitionsRule().run(make_context(parsed))
    assert results[0].rule_id == "ABBR-002"


def test_terminology_inconsistency_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_term",
        paragraphs=[
            ParsedParagraph(text="ABC-123 was supplied.", paragraph_index=0),
            ParsedParagraph(text="ABC123 was tested.", paragraph_index=1),
        ],
    )
    results = SimpleTerminologyInconsistencyRule().run(make_context(parsed))
    assert results[0].rule_id == "TERM-001"
