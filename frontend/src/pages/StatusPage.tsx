import { useEffect, useState } from "react";
import { Activity, AlertTriangle, CheckCircle2 } from "lucide-react";
import { api, getApiBaseUrl } from "../api/client";
import type { HealthStatus } from "../types/api";

export function StatusPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadHealth() {
    setError(null);
    try {
      setHealth(await api.health());
    } catch (err) {
      setHealth(null);
      setError(err instanceof Error ? err.message : "Unable to connect to backend.");
    }
  }

  useEffect(() => {
    void loadHealth();
  }, []);

  const apiBaseUrl = getApiBaseUrl() || "Not configured";
  const healthy = health?.status === "ok";

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">System Status</h1>
          <p className="mt-2 text-sm text-muted">Local service health and runtime configuration.</p>
        </div>
        <button className="button-secondary" type="button" onClick={loadHealth}>
          Check again
        </button>
      </div>

      <div className="rounded-lg border border-line bg-white p-5">
        <div className="flex items-start gap-3">
          {healthy ? (
            <CheckCircle2 aria-hidden="true" className="mt-0.5 h-5 w-5 text-green-700" />
          ) : error ? (
            <AlertTriangle aria-hidden="true" className="mt-0.5 h-5 w-5 text-red-700" />
          ) : (
            <Activity aria-hidden="true" className="mt-0.5 h-5 w-5 text-accent" />
          )}
          <div>
            <h2 className="text-sm font-semibold">Backend connection</h2>
            <p className="mt-1 text-sm text-muted">API_BASE_URL: {apiBaseUrl}</p>
          </div>
        </div>

        {error ? (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            <div className="font-medium">Backend is not reachable.</div>
            <div className="mt-1">Request failed: {error}</div>
            <div className="mt-1">Check that the backend is running at {apiBaseUrl}.</div>
          </div>
        ) : null}

        {health ? (
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            <StatusItem label="Service" value={health.service} />
            <StatusItem label="Status" value={health.status} />
            <StatusItem label="Backend port" value={String(health.port)} />
            <StatusItem label="Version" value={health.version} />
            <StatusItem label="Database" value={health.database.status} />
            <StatusItem label="Upload storage" value={health.upload_storage.writable ? "writable" : "not writable"} />
            <StatusItem label="AI API key" value={health.ai_api_key.present ? "configured" : "not configured"} />
            <StatusItem label="Timestamp" value={health.timestamp} />
          </div>
        ) : null}

        {health?.database.status === "disconnected" ? (
          <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Database disconnected: {health.database.error || "No error detail provided."}
          </div>
        ) : null}
        {health?.upload_storage.error ? (
          <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Upload storage issue: {health.upload_storage.error}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-surface px-3 py-2 text-sm">
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 font-medium break-words">{value}</div>
    </div>
  );
}
