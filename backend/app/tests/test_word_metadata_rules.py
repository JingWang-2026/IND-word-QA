from app.rules.word_metadata_rules import HeaderFooterVersionRule, RemainingCommentsRule, TrackedChangesRule
from app.schemas.parsed_content import ParsedComment, ParsedDocument, ParsedTextBlock, TrackedChange
from app.tests.rule_test_utils import make_context


def test_header_footer_version_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_version",
        headers=[ParsedTextBlock(block_type="header", text="Version 1.0")],
        footers=[ParsedTextBlock(block_type="footer", text="v1.1")],
    )
    results = HeaderFooterVersionRule().run(make_context(parsed))
    assert results[0].rule_id == "WORD-001"


def test_remaining_comments_rule() -> None:
    parsed = ParsedDocument(document_id="doc_comment", comments=[ParsedComment(text="Please resolve.", author="QA")])
    results = RemainingCommentsRule().run(make_context(parsed))
    assert results[0].rule_id == "WORD-002"


def test_tracked_changes_rule() -> None:
    parsed = ParsedDocument(document_id="doc_changes", tracked_changes=[TrackedChange(change_type="ins", text="new")])
    results = TrackedChangesRule().run(make_context(parsed))
    assert results[0].rule_id == "WORD-003"
