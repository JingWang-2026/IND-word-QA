from pydantic import BaseModel, Field


class ParsedTextBlock(BaseModel):
    text: str
    block_type: str
    index: int | None = None
    style_name: str | None = None
    section_number: str | None = None
    section_title: str | None = None
    metadata: dict = Field(default_factory=dict)


class ParsedParagraph(ParsedTextBlock):
    block_type: str = "paragraph"
    paragraph_index: int


class ParsedHeading(ParsedTextBlock):
    block_type: str = "heading"
    paragraph_index: int
    level: int | None = None


class ParsedTableData(BaseModel):
    table_index: int
    rows: list[list[str]]
    markdown: str
    caption: str | None = None
    section_number: str | None = None
    section_title: str | None = None


class ParsedComment(BaseModel):
    comment_id: str | None = None
    author: str | None = None
    date: str | None = None
    text: str


class TrackedChange(BaseModel):
    change_type: str
    author: str | None = None
    date: str | None = None
    text: str
    xml_location_hint: str | None = None


class ParsedDocument(BaseModel):
    document_id: str
    metadata: dict = Field(default_factory=dict)
    paragraphs: list[ParsedParagraph] = Field(default_factory=list)
    headings: list[ParsedHeading] = Field(default_factory=list)
    tables: list[ParsedTableData] = Field(default_factory=list)
    headers: list[ParsedTextBlock] = Field(default_factory=list)
    footers: list[ParsedTextBlock] = Field(default_factory=list)
    comments: list[ParsedComment] = Field(default_factory=list)
    tracked_changes: list[TrackedChange] = Field(default_factory=list)
    hidden_text: list[ParsedTextBlock] = Field(default_factory=list)


class ParsedSummary(BaseModel):
    document_id: str
    paragraph_count: int
    heading_count: int
    table_count: int
    header_count: int
    footer_count: int
    comment_count: int
    tracked_change_count: int
    hidden_text_count: int
    metadata: dict = Field(default_factory=dict)
