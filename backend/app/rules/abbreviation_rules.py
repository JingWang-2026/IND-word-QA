import re
from collections import defaultdict

from app.rules.base import BaseRule, RuleContext, RuleResult

ABBR_RE = re.compile(r"\b(AE|SAE|DLT|PK|PD|MTD|TEAE)\b")
DEFINITION_RE = re.compile(r"(?P<term>[A-Za-z][A-Za-z -]{2,80}?)\s*\(\s*(?P<abbr>[A-Z]{2,8})\s*\)")


class AbbreviationFirstDefinitionRule(BaseRule):
    rule_id = "ABBR-001"
    category = "Abbreviation"
    severity = "Medium"

    def run(self, context: RuleContext) -> list[RuleResult]:
        text_blocks = [(p.text, p.paragraph_index) for p in context.parsed_document.paragraphs]
        first_defs = set()
        for text, _ in text_blocks:
            for match in DEFINITION_RE.finditer(text):
                first_defs.add(match.group("abbr"))

        seen = set()
        results = []
        for text, paragraph_index in text_blocks:
            for match in ABBR_RE.finditer(text):
                abbr = match.group(1)
                if abbr in seen:
                    continue
                seen.add(abbr)
                definition_match = DEFINITION_RE.search(text)
                if definition_match and definition_match.group("abbr") == abbr and definition_match.start("abbr") >= match.start():
                    continue
                if abbr not in first_defs or not _has_definition_before_or_at(text, abbr, match.start()):
                    results.append(
                        RuleResult(
                            rule_id=self.rule_id,
                            severity=self.severity,
                            category=self.category,
                            title="Abbreviation first use is not defined",
                            description=f"The first detected use of {abbr} does not include a full-term definition.",
                            source_text=text,
                            suggestion=f"Define {abbr} at first use, for example full term ({abbr}).",
                            location={"paragraph_index": paragraph_index},
                            confidence=0.75,
                        )
                    )
        return results


class AbbreviationMultipleDefinitionsRule(BaseRule):
    rule_id = "ABBR-002"
    category = "Abbreviation"
    severity = "Medium"

    def run(self, context: RuleContext) -> list[RuleResult]:
        definitions: dict[str, set[str]] = defaultdict(set)
        evidence = defaultdict(list)
        for paragraph in context.parsed_document.paragraphs:
            for match in DEFINITION_RE.finditer(paragraph.text):
                abbr = match.group("abbr")
                term = " ".join(match.group("term").split()).strip().lower()
                definitions[abbr].add(term)
                evidence[abbr].append({"term": term, "paragraph_index": paragraph.paragraph_index})

        results = []
        for abbr, terms in definitions.items():
            if len(terms) > 1:
                results.append(
                    RuleResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        category=self.category,
                        title="Abbreviation has multiple definitions",
                        description=f"{abbr} is defined with multiple full terms.",
                        source_text=f"{abbr}: {', '.join(sorted(terms))}",
                        suggestion=f"Use one definition for {abbr}, or confirm the abbreviation is intentional.",
                        evidence=evidence[abbr],
                        confidence=0.85,
                    )
                )
        return results


def _has_definition_before_or_at(text: str, abbr: str, position: int) -> bool:
    for match in DEFINITION_RE.finditer(text):
        if match.group("abbr") == abbr and match.start("abbr") >= position:
            return True
    return False
