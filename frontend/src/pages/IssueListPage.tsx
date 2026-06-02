import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Download, SlidersHorizontal } from "lucide-react";
import { api } from "../api/client";
import type { DocumentRecord, QAIssue } from "../types/api";

const severities = ["", "Critical", "High", "Medium", "Low"];
const statuses = ["", "Open", "Confirmed", "False Positive", "Resolved"];

export function IssueListPage() {
  const { projectId } = useParams();
  const [issues, setIssues] = useState<QAIssue[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [filters, setFilters] = useState({ severity: "", category: "", document_id: "", status: "" });
  const [error, setError] = useState<string | null>(null);

  const documentNames = useMemo(
    () => Object.fromEntries(documents.map((document) => [document.id, document.filename])),
    [documents],
  );

  useEffect(() => {
    if (!projectId) return;
    api
      .listDocuments(projectId)
      .then(setDocuments)
      .catch(() => setDocuments([]));
  }, [projectId]);

  useEffect(() => {
    if (!projectId) return;
    api
      .listIssues(projectId, filters)
      .then(setIssues)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load issues."));
  }, [projectId, filters]);

  if (!projectId) return null;

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">QA issues</h1>
          <p className="mt-1 text-sm text-muted">{issues.length} issues in the current view.</p>
        </div>
        <a className="button-secondary gap-2" href={api.exportIssuesUrl(projectId, filters)}>
          <Download aria-hidden="true" className="h-4 w-4" />
          Export Excel
        </a>
      </div>

      <div className="grid gap-3 rounded-lg border border-line bg-white p-4 md:grid-cols-4">
        <label className="text-sm font-medium">
          Severity
          <select
            className="field mt-1"
            value={filters.severity}
            onChange={(event) => setFilters((current) => ({ ...current, severity: event.target.value }))}
          >
            {severities.map((severity) => (
              <option key={severity} value={severity}>
                {severity || "All"}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium">
          Category
          <input
            className="field mt-1"
            value={filters.category}
            onChange={(event) => setFilters((current) => ({ ...current, category: event.target.value }))}
            placeholder="Text, Numeric..."
          />
        </label>
        <label className="text-sm font-medium">
          Document
          <select
            className="field mt-1"
            value={filters.document_id}
            onChange={(event) => setFilters((current) => ({ ...current, document_id: event.target.value }))}
          >
            <option value="">All</option>
            {documents.map((document) => (
              <option key={document.id} value={document.id}>
                {document.filename}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium">
          Status
          <select
            className="field mt-1"
            value={filters.status}
            onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))}
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status || "All"}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="rounded-lg border border-line bg-white">
        <div className="flex items-center gap-2 border-b border-line px-4 py-3 text-sm font-medium">
          <SlidersHorizontal aria-hidden="true" className="h-4 w-4 text-accent" />
          Issue list
        </div>
        {error ? <p className="px-4 py-3 text-sm text-red-700">{error}</p> : null}
        {issues.length === 0 ? <p className="px-4 py-3 text-sm text-muted">No issues match the current filters.</p> : null}
        {issues.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Severity</th>
                  <th className="px-4 py-3 font-medium">Category</th>
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Document</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {issues.map((issue) => (
                  <tr key={issue.id}>
                    <td className="px-4 py-3">{issue.severity}</td>
                    <td className="px-4 py-3">{issue.category}</td>
                    <td className="max-w-md px-4 py-3">{issue.title}</td>
                    <td className="px-4 py-3">{issue.document_id ? documentNames[issue.document_id] || issue.document_id : ""}</td>
                    <td className="px-4 py-3">{issue.status}</td>
                    <td className="px-4 py-3">
                      <Link className="text-accent hover:underline" to={`/issues/${issue.id}`}>
                        Open
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </section>
  );
}
