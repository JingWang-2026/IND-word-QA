import re

from app.rules.base import BaseRule, RuleContext, RuleResult

VERSION_RE = re.compile(r"\b(?:Version\s*:?\s*|v)(?P<version>\d+(?:\.\d+)+)\b", re.IGNORECASE)


class HeaderFooterVersionRule(BaseRule):
    rule_id = "WORD-001"
    category = "Word Metadata"
    severity = "High"

    def run(self, context: RuleContext) -> list[RuleResult]:
        versions = {}
        for block in context.parsed_document.headers + context.parsed_document.footers:
            for match in VERSION_RE.finditer(block.text):
                versions.setdefault(match.group("version"), []).append(block.text)
        if len(versions) <= 1:
            return []
        return [
            RuleResult(
                rule_id=self.rule_id,
                severity=self.severity,
                category=self.category,
                title="Header/footer version inconsistency",
                description=f"Multiple version numbers were found in headers or footers: {', '.join(sorted(versions))}.",
                source_text=" | ".join(sorted({text for texts in versions.values() for text in texts})),
                suggestion="Use one document version consistently across all headers and footers.",
                location={"versions": sorted(versions)},
                evidence=[{"version": version, "texts": texts} for version, texts in versions.items()],
                confidence=0.95,
            )
        ]


class RemainingCommentsRule(BaseRule):
    rule_id = "WORD-002"
    category = "Word Metadata"
    severity = "High"

    def run(self, context: RuleContext) -> list[RuleResult]:
        return [
            RuleResult(
                rule_id=self.rule_id,
                severity=self.severity,
                category=self.category,
                title="Remaining Word comment",
                description="A Word comment remains in the document.",
                source_text=comment.text,
                suggestion="Resolve or delete the Word comment before finalization.",
                location={"comment_id": comment.comment_id, "author": comment.author},
                confidence=0.98,
            )
            for comment in context.parsed_document.comments
        ]


class TrackedChangesRule(BaseRule):
    rule_id = "WORD-003"
    category = "Word Metadata"
    severity = "High"

    def run(self, context: RuleContext) -> list[RuleResult]:
        return [
            RuleResult(
                rule_id=self.rule_id,
                severity=self.severity,
                category=self.category,
                title="Remaining tracked change",
                description=f"A Word tracked change remains in the document: {change.change_type}.",
                source_text=change.text or change.change_type,
                suggestion="Accept or reject tracked changes before finalization.",
                location={"change_type": change.change_type, "author": change.author, "xml_location_hint": change.xml_location_hint},
                confidence=0.98,
            )
            for change in context.parsed_document.tracked_changes
        ]
