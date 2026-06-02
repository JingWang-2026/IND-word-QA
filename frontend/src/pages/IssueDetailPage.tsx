import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import type { QAIssue } from "../types/api";

const statuses = ["Open", "Confirmed", "False Positive", "Resolved"];

export function IssueDetailPage() {
  const { issueId } = useParams();
  const [issue, setIssue] = useState<QAIssue | null>(null);
  const [status, setStatus] = useState("Open");
  const [comment, setComment] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!issueId) return;
    api.getIssue(issueId).then((data) => {
      setIssue(data);
      setStatus(data.status);
      setComment(data.reviewer_comment || "");
    });
  }, [issueId]);

  async function save() {
    if (!issueId) return;
    const updated = await api.updateIssue(issueId, { status, reviewer_comment: comment });
    setIssue(updated);
    setMessage("Issue updated.");
  }

  if (!issue) return <p className="text-sm text-muted">Loading issue...</p>;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <section className="rounded-lg border border-line bg-white p-5">
        <div className="flex flex-wrap gap-2 text-sm text-muted">
          <span>{issue.severity}</span>
          <span>{issue.category}</span>
          {issue.rule_id ? <span>{issue.rule_id}</span> : null}
        </div>
        <h1 className="mt-3 text-2xl font-semibold">{issue.title}</h1>
        <dl className="mt-6 space-y-5 text-sm">
          <Detail label="Description" value={issue.description} />
          <Detail label="Source Text" value={issue.source_text || ""} />
          <Detail label="Suggestion" value={issue.suggestion || ""} />
          <Detail label="Location" value={issue.location_json || ""} />
          <Detail label="Evidence" value={issue.evidence_json || ""} />
        </dl>
      </section>
      <aside className="rounded-lg border border-line bg-white p-5">
        <h2 className="text-lg font-semibold">Review</h2>
        <label className="mt-4 block text-sm font-medium">
          Status
          <select className="field mt-1" value={status} onChange={(event) => setStatus(event.target.value)}>
            {statuses.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label className="mt-4 block text-sm font-medium">
          Reviewer comment
          <textarea className="field mt-1 min-h-32" value={comment} onChange={(event) => setComment(event.target.value)} />
        </label>
        <button className="button-primary mt-4 w-full" type="button" onClick={save}>
          Save review
        </button>
        {message ? <p className="mt-3 text-sm text-muted">{message}</p> : null}
      </aside>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-medium">{label}</dt>
      <dd className="mt-1 whitespace-pre-wrap rounded-md bg-surface p-3 text-muted">{value || "Not provided"}</dd>
    </div>
  );
}
