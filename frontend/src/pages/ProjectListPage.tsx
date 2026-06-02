import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { api } from "../api/client";
import type { Project } from "../types/api";

export function ProjectListPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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
    try {
      await api.createProject({ name: name.trim(), description: description.trim() || undefined });
      setName("");
      setDescription("");
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project.");
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[360px_1fr]">
      <section>
        <h1 className="text-2xl font-semibold">Projects</h1>
        <p className="mt-2 max-w-prose text-sm leading-6 text-muted">
          Create a QA workspace for one IND or medical writing package.
        </p>
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
          <button className="button-primary gap-2" type="submit">
            <Plus aria-hidden="true" className="h-4 w-4" />
            Create project
          </button>
        </form>
      </section>

      <section className="rounded-lg border border-line bg-white">
        <div className="border-b border-line px-4 py-3 text-sm font-medium">Project list</div>
        {error ? <p className="px-4 py-3 text-sm text-red-700">{error}</p> : null}
        {loading ? <p className="px-4 py-3 text-sm text-muted">Loading projects...</p> : null}
        {!loading && projects.length === 0 ? <p className="px-4 py-3 text-sm text-muted">No projects yet.</p> : null}
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
  );
}
