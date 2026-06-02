import re
from collections import Counter, defaultdict

from app.rules.base import BaseRule, RuleContext, RuleResult

TERM_RE = re.compile(r"\b[A-Z]{2,}[\s-]?\d{2,}\b")


class SimpleTerminologyInconsistencyRule(BaseRule):
    rule_id = "TERM-001"
    category = "Terminology"
    severity = "Medium"

    def run(self, context: RuleContext) -> list[RuleResult]:
        variants: dict[str, Counter[str]] = defaultdict(Counter)
        for paragraph in context.parsed_document.paragraphs:
            for match in TERM_RE.finditer(paragraph.text):
                term = match.group(0)
                variants[_normalize(term)][term] += 1

        results = []
        for normalized, counts in variants.items():
            if len(counts) <= 1:
                continue
            preferred = counts.most_common(1)[0][0]
            results.append(
                RuleResult(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    category=self.category,
                    title="Terminology spelling inconsistency",
                    description=f"Similar term variants were found for {normalized}: {', '.join(sorted(counts))}.",
                    source_text=", ".join(sorted(counts)),
                    suggestion=f"Consider using {preferred} consistently.",
                    evidence=[{"variant": variant, "count": count} for variant, count in counts.items()],
                    confidence=0.75,
                )
            )
        return results


def _normalize(term: str) -> str:
    return re.sub(r"[\s-]+", "", term).upper()
