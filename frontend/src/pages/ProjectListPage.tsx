import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FolderOpen, Plus } from "lucide-react";
import { api } from "../api/client";
import type { Project } from "../types/api";

export function ProjectListPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  async function loadProjects() {
    setLoading(true);
    setError(null);
    try {
      setProjects(await api.listProjects());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadProjects();
  }, []);

  async function createProject(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    setError(null);
    setSuccess(null);
    setCreating(true);
    try {
      const project = await api.createProject({ name: name.trim(), description: description.trim() || undefined });
      setName("");
      setDescription("");
      await loadProjects();
      setSuccess(`Project created: ${project.name}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold">Word Report QA Assistant</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
            Create a project, upload .docx reports, run deterministic QA checks, and export a reviewer-ready issue log.
          </p>
        </div>
        <Link className="button-secondary" to="/status">
          System Status
        </Link>
      </section>

      <div className="grid gap-8 lg:grid-cols-[380px_1fr]">
        <section>
          <h2 className="text-lg font-semibold">Create project</h2>
          <form onSubmit={createProject} className="mt-6 space-y-3 rounded-lg border border-line bg-white p-4">
            <label className="block text-sm font-medium">
              Project name
              <input className="field mt-1" value={name} onChange={(event) => setName(event.target.value)} />
            </label>
            <label className="block text-sm font-medium">
              Description
              <textarea
                className="field mt-1 min-h-24"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />
            </label>
            <button className="button-primary gap-2" type="submit" disabled={creating || !name.trim()}>
              <Plus aria-hidden="true" className="h-4 w-4" />
              {creating ? "Creating..." : "Create project"}
            </button>
            {success ? <p className="text-sm text-green-700">{success}</p> : null}
          </form>
        </section>

        <section className="rounded-lg border border-line bg-white">
          <div className="flex items-center gap-2 border-b border-line px-4 py-3 text-sm font-medium">
            <FolderOpen aria-hidden="true" className="h-4 w-4 text-accent" />
            Project list
          </div>
          {error ? <p className="px-4 py-3 text-sm text-red-700">{error}</p> : null}
          {loading ? <p className="px-4 py-3 text-sm text-muted">Loading projects...</p> : null}
          {!loading && projects.length === 0 ? (
            <div className="px-4 py-10 text-center">
              <div className="text-sm font-medium">No projects yet</div>
              <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted">
                Create a project to start checking Word reports. Projects stay local on this machine.
              </p>
            </div>
          ) : null}
          <div className="divide-y divide-line">
            {projects.map((project) => (
              <Link key={project.id} to={`/projects/${project.id}`} className="block px-4 py-4 hover:bg-surface">
                <div className="font-medium">{project.name}</div>
                <div className="mt-1 text-sm text-muted">{project.description || "No description"}</div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
