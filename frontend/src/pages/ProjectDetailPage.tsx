import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Download, FileUp, Play, SearchCheck } from "lucide-react";
import { api } from "../api/client";
import type { DocumentRecord, ProjectDetail, QAIssue } from "../types/api";

const issueStatuses = ["Open", "Confirmed", "False Positive", "Resolved"];

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [issues, setIssues] = useState<QAIssue[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const documentNames = useMemo(
    () => Object.fromEntries(documents.map((document) => [document.id, document.filename])),
    [documents],
  );

  const issueCounts = useMemo(() => {
    const counts = { High: 0, Medium: 0, Low: 0 };
    for (const issue of issues) {
      if (issue.severity === "High") counts.High += 1;
      if (issue.severity === "Medium") counts.Medium += 1;
      if (issue.severity === "Low") counts.Low += 1;
    }
    return counts;
  }, [issues]);

  useEffect(() => {
    void refresh();
  }, [projectId]);

  async function refresh() {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const [projectData, documentData, issueData] = await Promise.all([
        api.getProject(projectId),
        api.listDocuments(projectId),
        api.listIssues(projectId),
      ]);
      setProject(projectData);
      setDocuments(documentData);
      setIssues(issueData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project.");
    } finally {
      setLoading(false);
    }
  }

  function chooseFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSuccess(null);
    setError(null);
    if (!file) {
      setSelectedFile(null);
      return;
    }
    if (!file.name.toLowerCase().endsWith(".docx")) {
      setSelectedFile(null);
      event.target.value = "";
      setError("Only .docx Word files are supported. .doc files are not allowed.");
      return;
    }
    setSelectedFile(file);
  }

  async function uploadSelectedFile() {
    if (!projectId || !selectedFile) return;
    setBusy("upload");
    setError(null);
    setSuccess(null);
    try {
      await api.uploadDocument(projectId, selectedFile);
      setSelectedFile(null);
      setSuccess(`Uploaded ${selectedFile.name}.`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setBusy(null);
    }
  }

  async function parseDocument(documentId: string) {
    setBusy(`parse:${documentId}`);
    setError(null);
    setSuccess(null);
    try {
      await api.parseDocument(documentId);
      setSuccess("Document parsed successfully.");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed.");
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  async function runDocumentQa(documentId: string) {
    setBusy(`qa:${documentId}`);
    setError(null);
    setSuccess(null);
    try {
      await api.runDocumentQa(documentId);
      setSuccess("QA completed for document.");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "QA run failed. Parse the document before running QA.");
    } finally {
      setBusy(null);
    }
  }

  async function runProjectQa() {
    if (!projectId) return;
    setBusy("qa:project");
    setError(null);
    setSuccess(null);
    try {
      await api.runProjectQa(projectId);
      setSuccess("Project QA completed.");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Project QA run failed.");
    } finally {
      setBusy(null);
    }
  }

  async function updateIssueStatus(issueId: string, status: string) {
    setBusy(`issue:${issueId}`);
    setError(null);
    setSuccess(null);
    try {
      const updated = await api.updateIssue(issueId, { status });
      setIssues((current) => current.map((issue) => (issue.id === issueId ? updated : issue)));
      setSuccess("Issue status updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update issue status.");
    } finally {
      setBusy(null);
    }
  }

  if (loading && !project) return <p className="text-sm text-muted">Loading project...</p>;
  if (!project) return <p className="text-sm text-red-700">{error || "Project not found."}</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link className="button-secondary mb-4 gap-2" to="/">
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            Back to projects
          </Link>
          <h1 className="text-2xl font-semibold">{project.name}</h1>
          <p className="mt-2 max-w-prose text-sm leading-6 text-muted">{project.description || "No description"}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="button-primary gap-2" type="button" onClick={runProjectQa} disabled={busy !== null}>
            <Play aria-hidden="true" className="h-4 w-4" />
            Run project QA
          </button>
          <Link className="button-secondary gap-2" to={`/projects/${project.id}/issues`}>
            <SearchCheck aria-hidden="true" className="h-4 w-4" />
            Full issue view
          </Link>
          <a className="button-secondary gap-2" href={api.exportIssuesUrl(project.id)}>
            <Download aria-hidden="true" className="h-4 w-4" />
            Export Excel
          </a>
        </div>
      </div>

      {error ? <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      {success ? <p className="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">{success}</p> : null}
      {busy ? <p className="text-sm text-muted">Working...</p> : null}

      <div className="grid gap-3 sm:grid-cols-4">
        <Metric label="Documents" value={documents.length} />
        <Metric label="Issues" value={issues.length} />
        <Metric label="High" value={issueCounts.High} />
        <Metric label="Medium / Low" value={`${issueCounts.Medium} / ${issueCounts.Low}`} />
      </div>

      <section className="rounded-lg border border-line bg-white p-4">
        <div className="flex items-center gap-2 text-sm font-medium">
          <FileUp aria-hidden="true" className="h-4 w-4 text-accent" />
          Upload Word document
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
          <label className="block text-sm font-medium">
            Select .docx file
            <input className="field mt-1" type="file" accept=".docx" onChange={chooseFile} disabled={busy !== null} />
          </label>
          <button className="button-primary" type="button" onClick={uploadSelectedFile} disabled={busy !== null || !selectedFile}>
            Upload
          </button>
        </div>
        {selectedFile ? (
          <p className="mt-2 text-sm text-muted">
            Selected: {selectedFile.name} ({formatBytes(selectedFile.size)})
          </p>
        ) : null}
      </section>

      <section className="rounded-lg border border-line bg-white">
        <div className="border-b border-line px-4 py-3 text-sm font-medium">Uploaded documents</div>
        {documents.length === 0 ? <p className="px-4 py-3 text-sm text-muted">No documents uploaded yet.</p> : null}
        {documents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">File name</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Uploaded</th>
                  <th className="px-4 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {documents.map((document) => (
                  <tr key={document.id}>
                    <td className="max-w-md px-4 py-3">
                      <div className="font-medium">{document.filename}</div>
                      {document.parse_error ? <div className="mt-1 text-red-700">{document.parse_error}</div> : null}
                    </td>
                    <td className="px-4 py-3">{formatBytes(document.file_size)}</td>
                    <td className="px-4 py-3">{document.status}</td>
                    <td className="px-4 py-3">{formatDate(document.created_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        <button
                          className="button-secondary"
                          type="button"
                          onClick={() => parseDocument(document.id)}
                          disabled={busy !== null || document.status === "parsing"}
                        >
                          Parse
                        </button>
                        <button
                          className="button-secondary"
                          type="button"
                          onClick={() => runDocumentQa(document.id)}
                          disabled={busy !== null || !["parsed", "qa_done"].includes(document.status)}
                        >
                          Run QA
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>

      <section className="rounded-lg border border-line bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3">
          <div className="text-sm font-medium">QA issue list</div>
          <div className="text-sm text-muted">
            High {issueCounts.High} / Medium {issueCounts.Medium} / Low {issueCounts.Low}
          </div>
        </div>
        {issues.length === 0 ? <p className="px-4 py-3 text-sm text-muted">No issues found.</p> : null}
        {issues.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Severity</th>
                  <th className="px-4 py-3 font-medium">Category</th>
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Document name</th>
                  <th className="px-4 py-3 font-medium">Section</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Source text</th>
                  <th className="px-4 py-3 font-medium">Suggestion</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {issues.map((issue) => (
                  <tr key={issue.id}>
                    <td className="px-4 py-3">{issue.severity}</td>
                    <td className="px-4 py-3">{issue.category}</td>
                    <td className="min-w-56 px-4 py-3">{issue.title}</td>
                    <td className="min-w-48 px-4 py-3">
                      {issue.document_id ? documentNames[issue.document_id] || issue.document_id : ""}
                    </td>
                    <td className="px-4 py-3">{formatIssueSection(issue)}</td>
                    <td className="px-4 py-3">
                      <select
                        className="field min-w-36"
                        value={issue.status}
                        onChange={(event) => updateIssueStatus(issue.id, event.target.value)}
                        disabled={busy !== null}
                      >
                        {issueStatuses.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="min-w-64 max-w-md px-4 py-3">{issue.source_text || ""}</td>
                    <td className="min-w-64 max-w-md px-4 py-3">{issue.suggestion || ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-sm text-muted">{label}</div>
    </div>
  );
}

function formatBytes(bytes: number) {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function formatIssueSection(issue: QAIssue) {
  if (!issue.location_json) return "";
  try {
    const location = JSON.parse(issue.location_json) as {
      section_number?: string | null;
      section_title?: string | null;
      table_index?: number | null;
      row_index?: number | null;
      col_index?: number | null;
    };
    const section = [location.section_number, location.section_title].filter(Boolean).join(" ");
    if (section) return section;
    if (location.table_index !== undefined && location.table_index !== null) {
      return `Table ${location.table_index + 1}`;
    }
    return "";
  } catch {
    return "";
  }
}
