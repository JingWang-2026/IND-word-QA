import re
from collections import Counter

from app.rules.base import BaseRule, RuleContext, RuleResult

NA_VARIANTS = {"NA", "N/A", "N.A.", "Not applicable", "Not Applicable"}


class EmptyTableCellRule(BaseRule):
    rule_id = "TABLE-002"
    category = "Table"
    severity = "Medium"

    def run(self, context: RuleContext) -> list[RuleResult]:
        results = []
        for table in context.parsed_document.tables:
            for row_index, row in enumerate(table.rows):
                if all(not cell.strip() for cell in row):
                    continue
                for col_index, cell in enumerate(row):
                    if not cell.strip():
                        results.append(
                            RuleResult(
                                rule_id=self.rule_id,
                                severity=self.severity,
                                category=self.category,
                                title="Empty table cell",
                                description="A blank cell was found in a table.",
                                source_text=table.caption or f"Table {table.table_index + 1}",
                                suggestion='Fill the cell or use a standard notation such as "N/A".',
                                location={"table_index": table.table_index, "row_index": row_index, "col_index": col_index},
                                confidence=0.9,
                            )
                        )
        return results


class InconsistentNANotationRule(BaseRule):
    rule_id = "TABLE-003"
    category = "Table"
    severity = "Low"

    def run(self, context: RuleContext) -> list[RuleResult]:
        seen: Counter[str] = Counter()
        locations = []
        for table in context.parsed_document.tables:
            for row_index, row in enumerate(table.rows):
                for col_index, cell in enumerate(row):
                    if cell.strip() in NA_VARIANTS:
                        seen[cell.strip()] += 1
                        locations.append({"table_index": table.table_index, "row_index": row_index, "col_index": col_index})
        if len(seen) <= 1:
            return []
        return [
            RuleResult(
                rule_id=self.rule_id,
                severity=self.severity,
                category=self.category,
                title="Inconsistent N/A notation",
                description=f"Multiple not-applicable spellings were found: {', '.join(sorted(seen))}.",
                source_text=", ".join(sorted(seen)),
                suggestion='Use "N/A" consistently.',
                location={"locations": locations[:10]},
                evidence=[{"variant": variant, "count": count} for variant, count in seen.items()],
                confidence=0.95,
            )
        ]


class SimpleTableTotalRule(BaseRule):
    rule_id = "TABLE-001"
    category = "Table"
    severity = "High"

    def run(self, context: RuleContext) -> list[RuleResult]:
        results = []
        for table in context.parsed_document.tables:
            results.extend(self._check_two_column_table(table))
            results.extend(self._check_total_row(table))
        return results

    def _check_two_column_table(self, table) -> list[RuleResult]:
        numeric_rows = []
        total_value = None
        total_row_index = None
        for row_index, row in enumerate(table.rows):
            if len(row) < 2:
                continue
            label = row[0].strip()
            value = _number(row[1])
            if value is None:
                continue
            if _is_total_label(label):
                total_value = value
                total_row_index = row_index
            elif row_index != 0:
                numeric_rows.append(value)
        if total_value is None or len(numeric_rows) < 2:
            return []
        expected = sum(numeric_rows)
        if abs(expected - total_value) < 0.001:
            return []
        return [
            RuleResult(
                rule_id=self.rule_id,
                severity=self.severity,
                category=self.category,
                title="Table total mismatch",
                description=f"The table total is {total_value:g}, but the simple row sum is {expected:g}.",
                source_text=table.caption or table.markdown,
                suggestion="Verify component values or update the total.",
                location={"table_index": table.table_index, "row_index": total_row_index},
                confidence=0.85,
            )
        ]

    def _check_total_row(self, table) -> list[RuleResult]:
        results = []
        if len(table.rows) < 3:
            return results
        width = max(len(row) for row in table.rows)
        if width <= 2:
            return results
        total_rows = [idx for idx, row in enumerate(table.rows) if row and _is_total_label(row[0])]
        for total_row_index in total_rows:
            for col_index in range(1, width):
                values = []
                for row_index, row in enumerate(table.rows):
                    if row_index == 0 or row_index == total_row_index or col_index >= len(row):
                        continue
                    value = _number(row[col_index])
                    if value is not None:
                        values.append(value)
                total_value = _number(table.rows[total_row_index][col_index]) if col_index < len(table.rows[total_row_index]) else None
                if total_value is None or len(values) < 2:
                    continue
                expected = sum(values)
                if abs(expected - total_value) >= 0.001:
                    results.append(
                        RuleResult(
                            rule_id=self.rule_id,
                            severity=self.severity,
                            category=self.category,
                            title="Table total mismatch",
                            description=f"The table total is {total_value:g}, but the simple column sum is {expected:g}.",
                            source_text=table.caption or table.markdown,
                            suggestion="Verify component values or update the total.",
                            location={"table_index": table.table_index, "row_index": total_row_index, "col_index": col_index},
                            confidence=0.85,
                        )
                    )
        return results


def _is_total_label(text: str) -> bool:
    return bool(re.search(r"\b(total|overall)\b|合计", text, re.IGNORECASE))


def _number(text: str) -> float | None:
    cleaned = text.strip().replace(",", "")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", cleaned):
        return None
    return float(cleaned)
