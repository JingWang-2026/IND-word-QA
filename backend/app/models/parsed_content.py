from sqlmodel import Field, SQLModel


class ParsedBlock(SQLModel, table=True):
    id: str = Field(primary_key=True)
    document_id: str = Field(index=True, foreign_key="document.id")
    block_type: str
    text: str
    section_number: str | None = None
    section_title: str | None = None
    paragraph_index: int | None = None
    table_index: int | None = None
    row_index: int | None = None
    col_index: int | None = None
    style_name: str | None = None
    metadata_json: str | None = None


class ParsedTable(SQLModel, table=True):
    id: str = Field(primary_key=True)
    document_id: str = Field(index=True, foreign_key="document.id")
    table_index: int
    caption: str | None = None
    section_number: str | None = None
    section_title: str | None = None
    data_json: str
    markdown: str
