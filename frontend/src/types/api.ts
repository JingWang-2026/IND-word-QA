export type Project = {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectDetail = Project & {
  document_count: number;
  issue_count: number;
  issue_counts_by_severity: Record<string, number>;
};

export type DocumentRecord = {
  id: string;
  project_id: string;
  filename: string;
  file_size: number;
  status: string;
  parse_error: string | null;
  created_at: string;
  updated_at: string;
};

export type QAIssue = {
  id: string;
  project_id: string;
  document_id: string | null;
  severity: string;
  category: string;
  rule_id: string | null;
  title: string;
  description: string;
  source_text: string | null;
  suggestion: string | null;
  location_json: string | null;
  evidence_json: string | null;
  status: string;
  reviewer_comment: string | null;
  confidence: number | null;
  created_at: string;
  updated_at: string;
};
