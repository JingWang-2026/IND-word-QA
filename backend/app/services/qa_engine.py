from __future__ import annotations

import json
import logging
from uuid import uuid4

from sqlmodel import Session, select

from app.models.document import Document
from app.models.issue import QAIssue
from app.models.parsed_content import ParsedBlock, ParsedTable
from app.rules import default_rules
from app.rules.base import BaseRule, RuleContext, RuleResult
from app.schemas.parsed_content import (
    ParsedComment,
    ParsedDocument,
    ParsedHeading,
    ParsedParagraph,
    ParsedTableData,
    ParsedTextBlock,
    TrackedChange,
)

logger = logging.getLogger(__name__)


class QAEngine:
    def __init__(self, rules: list[BaseRule] | None = None):
        self.rules = rules if rules is not None else default_rules()

    def run_document_qa(self, context: RuleContext) -> list[RuleResult]:
        results: list[RuleResult] = []
        for rule in self.rules:
            try:
                results.extend(rule.run(context))
            except Exception:
                logger.exception("QA rule failed: %s", rule.rule_id)
        return self.deduplicate(results)

    def deduplicate(self, results: list[RuleResult]) -> list[RuleResult]:
        seen: set[str] = set()
        deduped: list[RuleResult] = []
        for result in results:
            key = json.dumps(
                {
                    "rule_id": result.rule_id,
                    "source_text": result.source_text,
                    "location": result.location,
                },
                sort_keys=True,
                ensure_ascii=False,
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(result)
        return deduped

    def save_results(
        self,
        session: Session,
        project_id: str,
        document_id: str,
        results: list[RuleResult],
        replace_existing: bool = True,
    ) -> list[QAIssue]:
        if replace_existing:
            existing = session.exec(select(QAIssue).where(QAIssue.document_id == document_id)).all()
            for issue in existing:
                session.delete(issue)

        issues = []
        for result in results:
            issue = QAIssue(
                id=f"QA-{uuid4().hex[:10].upper()}",
                project_id=project_id,
                document_id=document_id,
                severity=result.severity,
                category=result.category,
                rule_id=result.rule_id,
                title=result.title,
                description=result.description,
                source_text=result.source_text,
                suggestion=result.suggestion,
                location_json=json.dumps(result.location or {}, ensure_ascii=False),
                evidence_json=json.dumps(result.evidence, ensure_ascii=False),
                status="Open",
                confidence=result.confidence,
            )
            session.add(issue)
            issues.append(issue)
        return issues


class ParsedDocumentRepository:
    def load(self, session: Session, document: Document) -> ParsedDocument:
        blocks = list(session.exec(select(ParsedBlock).where(ParsedBlock.document_id == document.id)).all())
        tables = list(session.exec(select(ParsedTable).where(ParsedTable.document_id == document.id)).all())
        parsed = ParsedDocument(document_id=document.id, metadata={})

        for block in blocks:
            metadata = json.loads(block.metadata_json) if block.metadata_json else {}
            if block.block_type == "metadata":
                parsed.metadata = json.loads(block.text) if block.text else {}
            elif block.block_type == "paragraph":
                parsed.paragraphs.append(
                    ParsedParagraph(
                        text=block.text,
                        paragraph_index=block.paragraph_index or 0,
                        index=block.paragraph_index,
                        style_name=block.style_name,
                        section_number=block.section_number,
                        section_title=block.section_title,
                    )
                )
            elif block.block_type == "heading":
                parsed.headings.append(
                    ParsedHeading(
                        text=block.text,
                        paragraph_index=block.paragraph_index or 0,
                        index=block.paragraph_index,
                        style_name=block.style_name,
                        section_number=block.section_number,
                        section_title=block.section_title,
                        level=metadata.get("level"),
                    )
                )
            elif block.block_type == "header":
                parsed.headers.append(ParsedTextBlock(block_type="header", text=block.text, metadata=metadata))
            elif block.block_type == "footer":
                parsed.footers.append(ParsedTextBlock(block_type="footer", text=block.text, metadata=metadata))
            elif block.block_type == "comment":
                parsed.comments.append(ParsedComment(text=block.text, **metadata))
            elif block.block_type == "tracked_change":
                parsed.tracked_changes.append(TrackedChange(text=block.text, **metadata))
            elif block.block_type == "hidden_text":
                parsed.hidden_text.append(ParsedTextBlock(block_type="hidden_text", text=block.text, metadata=metadata))

        for table in sorted(tables, key=lambda item: item.table_index):
            parsed.tables.append(
                ParsedTableData(
                    table_index=table.table_index,
                    rows=json.loads(table.data_json),
                    markdown=table.markdown,
                    caption=table.caption,
                    section_number=table.section_number,
                    section_title=table.section_title,
                )
            )

        parsed.paragraphs.sort(key=lambda item: item.paragraph_index)
        parsed.headings.sort(key=lambda item: item.paragraph_index)
        return parsed
