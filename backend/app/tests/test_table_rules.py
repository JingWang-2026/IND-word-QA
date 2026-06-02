from app.rules.table_rules import EmptyTableCellRule, InconsistentNANotationRule, SimpleTableTotalRule
from app.schemas.parsed_content import ParsedDocument, ParsedTableData
from app.tests.rule_test_utils import make_context


def test_table_total_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_table_total",
        tables=[
            ParsedTableData(
                table_index=0,
                rows=[["Sex", "Count"], ["Male", "12"], ["Female", "9"], ["Total", "20"]],
                markdown="",
            )
        ],
    )
    results = SimpleTableTotalRule().run(make_context(parsed))
    assert results[0].rule_id == "TABLE-001"


def test_empty_table_cell_rule() -> None:
    parsed = ParsedDocument(document_id="doc_empty_cell", tables=[ParsedTableData(table_index=0, rows=[["A", ""]], markdown="")])
    results = EmptyTableCellRule().run(make_context(parsed))
    assert results[0].rule_id == "TABLE-002"


def test_inconsistent_na_notation_rule() -> None:
    parsed = ParsedDocument(
        document_id="doc_na",
        tables=[ParsedTableData(table_index=0, rows=[["N/A"], ["NA"], ["Not Applicable"]], markdown="")],
    )
    results = InconsistentNANotationRule().run(make_context(parsed))
    assert results[0].rule_id == "TABLE-003"
