import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session, col, select

from app.core.database import get_session
from app.models.document import Document
from app.models.parsed_content import ParsedBlock, ParsedTable
from app.models.project import Project
from app.schemas.document import DocumentRead
from app.schemas.parsed_content import ParsedSummary
from app.services.docx_parser import DocxParserService
from app.services.storage_service import StorageService

router = APIRouter(tags=["documents"])


@router.post("/api/projects/{project_id}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> Document:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    filename = file.filename or ""
    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .docx files are supported.")

    try:
        stored_path, file_size = await StorageService().save_upload(project_id, file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)) from exc

    now = datetime.now(timezone.utc)
    document = Document(
        id=f"doc_{uuid4().hex}",
        project_id=project_id,
        filename=filename,
        stored_path=stored_path,
        file_size=file_size,
        status="uploaded",
    )
    project.updated_at = now
    session.add(document)
    session.add(project)
    session.commit()
    session.refresh(document)
    return document


@router.get("/api/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_documents(project_id: str, session: Session = Depends(get_session)) -> list[Document]:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return list(
        session.exec(
            select(Document).where(Document.project_id == project_id).order_by(col(Document.created_at).desc())
        ).all()
    )


@router.post("/api/documents/{document_id}/parse", response_model=ParsedSummary)
def parse_document(document_id: str, session: Session = Depends(get_session)) -> ParsedSummary:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if not Path(document.stored_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found.")

    parser = DocxParserService()
    document.status = "parsing"
    document.parse_error = None
    document.updated_at = datetime.now(timezone.utc)
    session.add(document)
    session.commit()

    try:
        parsed = parser.parse(document.id, document.stored_path)
        parser.save_to_database(session, parsed)
        document.status = "parsed"
        document.updated_at = datetime.now(timezone.utc)
        session.add(document)
        session.commit()
        return ParsedSummary(
            document_id=document.id,
            paragraph_count=len(parsed.paragraphs),
            heading_count=len(parsed.headings),
            table_count=len(parsed.tables),
            header_count=len(parsed.headers),
            footer_count=len(parsed.footers),
            comment_count=len(parsed.comments),
            tracked_change_count=len(parsed.tracked_changes),
            hidden_text_count=len(parsed.hidden_text),
            metadata=parsed.metadata,
        )
    except Exception as exc:
        session.rollback()
        document.status = "failed"
        document.parse_error = str(exc)
        document.updated_at = datetime.now(timezone.utc)
        session.add(document)
        session.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Parse failed: {exc}") from exc


@router.get("/api/documents/{document_id}/parsed-summary", response_model=ParsedSummary)
def get_parsed_summary(document_id: str, session: Session = Depends(get_session)) -> ParsedSummary:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    blocks = list(session.exec(select(ParsedBlock).where(ParsedBlock.document_id == document_id)).all())
    tables = list(session.exec(select(ParsedTable).where(ParsedTable.document_id == document_id)).all())
    metadata_block = next((block for block in blocks if block.block_type == "metadata"), None)
    metadata = json.loads(metadata_block.text) if metadata_block and metadata_block.text else {}

    return ParsedSummary(
        document_id=document_id,
        paragraph_count=sum(1 for block in blocks if block.block_type == "paragraph"),
        heading_count=sum(1 for block in blocks if block.block_type == "heading"),
        table_count=len(tables),
        header_count=sum(1 for block in blocks if block.block_type == "header"),
        footer_count=sum(1 for block in blocks if block.block_type == "footer"),
        comment_count=sum(1 for block in blocks if block.block_type == "comment"),
        tracked_change_count=sum(1 for block in blocks if block.block_type == "tracked_change"),
        hidden_text_count=sum(1 for block in blocks if block.block_type == "hidden_text"),
        metadata=metadata,
    )
