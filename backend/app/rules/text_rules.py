import re

from app.rules.base import BaseRule, RuleContext, RuleResult

DUPLICATE_WORD_RE = re.compile(r"\b([A-Za-z]+)\s+\1\b", re.IGNORECASE)


class DuplicateWordRule(BaseRule):
    rule_id = "TEXT-001"
    category = "Text"
    severity = "Low"

    def run(self, context: RuleContext) -> list[RuleResult]:
        results = []
        for block in list(context.parsed_document.paragraphs) + _table_cells(context):
            text = block["text"] if isinstance(block, dict) else block.text
            location = block["location"] if isinstance(block, dict) else {"paragraph_index": block.paragraph_index}
            if DUPLICATE_WORD_RE.search(text):
                results.append(
                    RuleResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        category=self.category,
                        title="Duplicated word",
                        description="A consecutive duplicated English word was found.",
                        source_text=text,
                        suggestion="Remove one duplicated word.",
                        location=location,
                        confidence=0.98,
                    )
                )
        return results


class RepeatedSpacesRule(BaseRule):
    rule_id = "TEXT-002"
    category = "Text"
    severity = "Low"

    def run(self, context: RuleContext) -> list[RuleResult]:
        results = []
        for block in list(context.parsed_document.paragraphs) + _table_cells(context):
            text = block["text"] if isinstance(block, dict) else block.text
            location = block["location"] if isinstance(block, dict) else {"paragraph_index": block.paragraph_index}
            if re.search(r"\S {2,}\S", text):
                results.append(
                    RuleResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        category=self.category,
                        title="Repeated spaces",
                        description="Multiple consecutive spaces were found inside text.",
                        source_text=text,
                        suggestion="Replace repeated spaces with a single space unless alignment is intentional.",
                        location=location,
                        confidence=0.9,
                    )
                )
        return results


def _table_cells(context: RuleContext) -> list[dict]:
    cells = []
    for table in context.parsed_document.tables:
        for row_index, row in enumerate(table.rows):
            for col_index, text in enumerate(row):
                cells.append(
                    {
                        "text": text,
                        "location": {
                            "table_index": table.table_index,
                            "row_index": row_index,
                            "col_index": col_index,
                            "section_number": table.section_number,
                            "section_title": table.section_title,
                        },
                    }
                )
    return cells
