from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    document_title: str
    page_number: int
    excerpt: str


class DocumentSummary(BaseModel):
    id: str
    title: str
    document_type: str
    language: str
    description: str
    tags: list[str]


class AnalysisField(BaseModel):
    name: str
    content: str | None
    value_type: str
    confidence: float | None


class QualityIssue(BaseModel):
    field: str
    reason: str
    message: str
    confidence: float | None = None


class QualityReport(BaseModel):
    status: str
    minimum_confidence: float
    issues: list[QualityIssue]

class PiiEntity(BaseModel):
    text: str
    category: str
    confidence: float

class DocumentDetail(DocumentSummary):
    extracted_text: str
    key_phrases: list[str]
    entities: list[str]
    image_descriptions: list[str]
    tables: list[list[list[str]]]
    analysis_fields: list[AnalysisField] = []
    quality: QualityReport | None = None
    pii_entities: list[PiiEntity] = []

class SearchResult(BaseModel):
    document: DocumentSummary
    score: float
    excerpt: str
    page_number: int


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class AskResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[Citation]


class HealthResponse(BaseModel):
    status: str
    environment: str


class MetricsSummary(BaseModel):
    requests: int
    blocked_requests: int
    average_latency_ms: float