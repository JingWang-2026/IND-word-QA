import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { FileCheck2 } from "lucide-react";
import "./styles.css";
import { ProjectListPage } from "./pages/ProjectListPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { IssueDetailPage } from "./pages/IssueDetailPage";
import { IssueListPage } from "./pages/IssueListPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-surface text-ink">
        <header className="border-b border-line bg-white">
          <div className="mx-auto flex max-w-6xl items-center gap-3 px-6 py-4">
            <FileCheck2 aria-hidden="true" className="h-6 w-6 text-accent" />
            <Link to="/" className="text-lg font-semibold">
              Word Report QA Assistant
            </Link>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">
          <Routes>
            <Route path="/" element={<ProjectListPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/projects/:projectId/issues" element={<IssueListPage />} />
            <Route path="/issues/:issueId" element={<IssueDetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
