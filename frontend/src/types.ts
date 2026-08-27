export type DocumentSummary = {
  id: string;
  title: string;
  document_type: string;
  language: string;
  description: string;
  tags: string[];
};

export type AnalysisField = {
  name: string;
  content: string | null;
  value_type: string;
  confidence: number | null;
};

export type QualityIssue = {
  field: string;
  reason: string;
  message: string;
  confidence: number | null;
};

export type QualityReport = {
  status: string;
  minimum_confidence: number;
  issues: QualityIssue[];
};

export type DocumentDetail = DocumentSummary & {
  extracted_text: string;
  key_phrases: string[];
  entities: string[];
  image_descriptions: string[];
  tables: string[][][];
  analysis_fields: AnalysisField[];
  quality: QualityReport | null;
  pii_entities: PiiEntity[];
};

export type Citation = {
  document_id: string;
  document_title: string;
  page_number: number;
  excerpt: string;
};

export type SearchResult = {
  document: DocumentSummary;
  score: number;
  excerpt: string;
  page_number: number;
};

export type SearchResponse = {
  query: string;
  total: number;
  results: SearchResult[];
};

export type AskResponse = {
  answer: string;
  grounded: boolean;
  citations: Citation[];
};

export type PiiEntity = {
  text: string;
  category: string;
  confidence: number;
};
