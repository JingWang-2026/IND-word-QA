from collections import defaultdict

from app.rules.base import BaseRule, RuleContext, RuleResult


class HeadingNumberingGapRule(BaseRule):
    rule_id = "HEAD-001"
    category = "Heading"
    severity = "Medium"

    def run(self, context: RuleContext) -> list[RuleResult]:
        groups: dict[str, list[tuple[int, object]]] = defaultdict(list)
        for heading in context.parsed_document.headings:
            if not heading.section_number:
                continue
            parts = heading.section_number.split(".")
            if not all(part.isdigit() for part in parts):
                continue
            parent = ".".join(parts[:-1])
            groups[parent].append((int(parts[-1]), heading))

        results = []
        for parent, items in groups.items():
            ordered = sorted(items, key=lambda item: item[0])
            previous = None
            for current, heading in ordered:
                if previous is not None and current > previous + 1:
                    missing = [str(number) for number in range(previous + 1, current)]
                    missing_label = ", ".join(f"{parent + '.' if parent else ''}{number}" for number in missing)
                    results.append(
                        RuleResult(
                            rule_id=self.rule_id,
                            severity=self.severity,
                            category=self.category,
                            title="Heading numbering gap",
                            description=f"Missing heading number: {missing_label}.",
                            source_text=heading.text,
                            suggestion=f"Add missing heading {missing_label}, or correct the numbering.",
                            location={"paragraph_index": heading.paragraph_index, "section_number": heading.section_number},
                            confidence=0.85,
                        )
                    )
                previous = current
        return results
