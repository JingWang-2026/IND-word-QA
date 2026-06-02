import re

from app.rules.base import BaseRule, RuleContext, RuleResult

PERCENT_RE = re.compile(
    r"(?P<n>\d+)\s*(?:/|of|out of)\s*(?P<N>\d+)[^%\n\r]{0,40}?\(\s*(?P<pct>\d+(?:\.\d+)?)\s*%\s*\)",
    re.IGNORECASE,
)


class PercentageCalculationRule(BaseRule):
    rule_id = "NUM-001"
    category = "Numeric"
    severity = "High"
    tolerance = 0.2

    def run(self, context: RuleContext) -> list[RuleResult]:
        results = []
        for text, location in _iter_text(context):
            for match in PERCENT_RE.finditer(text):
                n = int(match.group("n"))
                denominator = int(match.group("N"))
                if denominator == 0:
                    continue
                observed = float(match.group("pct"))
                expected = round(n / denominator * 100, 1)
                if abs(observed - expected) > self.tolerance:
                    source = match.group(0)
                    results.append(
                        RuleResult(
                            rule_id=self.rule_id,
                            severity=self.severity,
                            category=self.category,
                            title="Percentage calculation mismatch",
                            description=(
                                f"The percentage {observed:.1f}% does not match {n}/{denominator}. "
                                f"Expected percentage is {expected:.1f}%."
                            ),
                            source_text=source,
                            suggestion=f"Change {observed:.1f}% to {expected:.1f}%, or verify numerator/denominator.",
                            location=location,
                            confidence=0.98,
                        )
                    )
        return results


def _iter_text(context: RuleContext):
    for paragraph in context.parsed_document.paragraphs:
        yield paragraph.text, {
            "paragraph_index": paragraph.paragraph_index,
            "section_number": paragraph.section_number,
            "section_title": paragraph.section_title,
        }
    for table in context.parsed_document.tables:
        for row_index, row in enumerate(table.rows):
            for col_index, text in enumerate(row):
                yield text, {"table_index": table.table_index, "row_index": row_index, "col_index": col_index}
