import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { FileUp, Play, SearchCheck } from "lucide-react";
import { api } from "../api/client";
import type { DocumentRecord, ProjectDetail } from "../types/api";

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    const id = projectId;
    async function load() {
      try {
        const [projectData, documentData] = await Promise.all([api.getProject(id), api.listDocuments(id)]);
        setProject(projectData);
        setDocuments(documentData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load project.");
      }
    }
    void load();
  }, [projectId]);

  async function refresh() {
    if (!projectId) return;
    const [projectData, documentData] = await Promise.all([api.getProject(projectId), api.listDocuments(projectId)]);
    setProject(projectData);
    setDocuments(documentData);
  }

  async function upload(event: React.ChangeEvent<HTMLInputElement>) {
    if (!projectId || !event.target.files?.[0]) return;
    setBusy("upload");
    setError(null);
    try {
      await api.uploadDocument(projectId, event.target.files[0]);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setBusy(null);
      event.target.value = "";
    }
  }

  async function parseDocument(documentId: string) {
    setBusy(documentId);
    setError(null);
    try {
      await api.parseDocument(documentId);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed.");
    } finally {
      setBusy(null);
    }
  }

  async function runQa() {
    if (!projectId) return;
    setBusy("qa");
    setError(null);
    try {
      await api.runProjectQa(projectId);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "QA run failed.");
    } finally {
      setBusy(null);
    }
  }

  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!project) return <p className="text-sm text-muted">Loading project...</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{project.name}</h1>
          <p className="mt-2 max-w-prose text-sm leading-6 text-muted">{project.description || "No description"}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <label className="button-secondary cursor-pointer gap-2">
            <FileUp aria-hidden="true" className="h-4 w-4" />
            Upload docx
            <input className="sr-only" type="file" accept=".docx" onChange={upload} disabled={busy !== null} />
          </label>
          <button className="button-primary gap-2" type="button" onClick={runQa} disabled={busy !== null}>
            <Play aria-hidden="true" className="h-4 w-4" />
            Run QA
          </button>
          <Link className="button-secondary gap-2" to={`/projects/${project.id}/issues`}>
            <SearchCheck aria-hidden="true" className="h-4 w-4" />
            View issues
          </Link>
        </div>
      </div>
      {error ? <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Documents" value={project.document_count} />
        <Metric label="Issues" value={project.issue_count} />
        <Metric label="High issues" value={project.issue_counts_by_severity.High ?? 0} />
      </div>

      <section className="rounded-lg border border-line bg-white">
        <div className="border-b border-line px-4 py-3 text-sm font-medium">Uploaded documents</div>
        {documents.length === 0 ? <p className="px-4 py-3 text-sm text-muted">No documents uploaded yet.</p> : null}
        <div className="divide-y divide-line">
          {documents.map((document) => (
            <div key={document.id} className="grid gap-3 px-4 py-3 sm:grid-cols-[1fr_auto_auto] sm:items-center">
              <div>
                <span className="font-medium">{document.filename}</span>
                {document.parse_error ? <div className="mt-1 text-sm text-red-700">{document.parse_error}</div> : null}
              </div>
              <span className="text-sm text-muted">{document.status}</span>
              <button
                className="button-secondary"
                type="button"
                onClick={() => parseDocument(document.id)}
                disabled={busy !== null || document.status === "parsing"}
              >
                Parse
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-sm text-muted">{label}</div>
    </div>
  );
}
