import re

from app.rules.base import BaseRule, RuleContext, RuleResult

REF_RE = re.compile(r"\b(?P<kind>Table|Figure)\s+(?P<num>\d+(?:-\d+)?)\b", re.IGNORECASE)


class MissingTableFigureReferenceRule(BaseRule):
    rule_id = "REF-001"
    category = "Reference"
    severity = "Medium"

    def run(self, context: RuleContext) -> list[RuleResult]:
        captions = set()
        for table in context.parsed_document.tables:
            if table.caption:
                match = REF_RE.search(table.caption)
                if match:
                    captions.add(_key(match))
        for paragraph in context.parsed_document.paragraphs:
            if re.match(r"^\s*(Table|Figure)\s+\d+(?:-\d+)?[\.:]", paragraph.text, re.IGNORECASE):
                match = REF_RE.search(paragraph.text)
                if match:
                    captions.add(_key(match))

        results = []
        for paragraph in context.parsed_document.paragraphs:
            for match in REF_RE.finditer(paragraph.text):
                if _key(match) not in captions:
                    source = match.group(0)
                    results.append(
                        RuleResult(
                            rule_id=self.rule_id,
                            severity=self.severity,
                            category=self.category,
                            title="Referenced table or figure not found",
                            description=f"{source} is referenced, but no matching caption was found.",
                            source_text=paragraph.text,
                            suggestion=f"Add a caption for {source}, or correct the reference.",
                            location={"paragraph_index": paragraph.paragraph_index},
                            confidence=0.8,
                        )
                    )
        return results


def _key(match: re.Match) -> str:
    return f"{match.group('kind').lower()} {match.group('num')}"
