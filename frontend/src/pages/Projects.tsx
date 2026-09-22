import React, { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus, FolderKanban, Globe, Github, FileArchive, Trash2, Search } from "lucide-react";
import { createProject, deleteProject, listProjects } from "../services/api";
import type { ProjectSummary, TargetType } from "../types";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { StatusBadge } from "../components/StatusBadge";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { useToast } from "../hooks/useToast";
import { formatDate } from "../lib/utils";

const TARGET_ICONS: Record<TargetType, typeof Globe> = {
  website: Globe,
  github: Github,
  zip: FileArchive,
};

const TARGET_LABELS: Record<TargetType, string> = {
  website: "Website",
  github: "GitHub",
  zip: "ZIP Upload",
};

export default function Projects() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [modalOpen, setModalOpen] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<ProjectSummary | null>(null);
  const [search, setSearch] = useState("");

  const { data: projects, isLoading } = useQuery({ queryKey: ["projects"], queryFn: listProjects });

  const filtered = useMemo(() => {
    if (!projects) return [];
    const q = search.trim().toLowerCase();
    if (!q) return projects;
    return projects.filter((p) => p.name.toLowerCase().includes(q) || p.target_value.toLowerCase().includes(q));
  }, [projects, search]);

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      showToast("Project created", "success");
      setModalOpen(false);
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      showToast("Project deleted", "success");
      setPendingDelete(null);
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-page-title text-ink-primary">Projects</h1>
          <p className="text-sm text-ink-tertiary mt-1">Security workspaces for the applications and codebases you're analyzing.</p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-1.5">
          <Plus className="h-4 w-4" />
          New project
        </button>
      </div>

      {!isLoading && projects && projects.length > 0 && (
        <div className="relative max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-ink-tertiary" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search projects…"
            className="input-field pl-8"
          />
        </div>
      )}

      {isLoading ? (
        <div className="card p-5 space-y-3">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : !projects || projects.length === 0 ? (
        <div className="card">
          <EmptyState
            icon={FolderKanban}
            title="No projects yet"
            description="Create your first project to begin organizing security analysis for a website, GitHub repo, or ZIP upload."
            action={
              <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-1.5">
                <Plus className="h-4 w-4" />
                New project
              </button>
            }
          />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card">
          <EmptyState icon={Search} title="No projects match your search" description="Try a different name or target." />
        </div>
      ) : (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Target</th>
                  <th>Findings</th>
                  <th>Last scan</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((project) => {
                  const Icon = TARGET_ICONS[project.target_type];
                  return (
                    <tr key={project.id} className="group">
                      <td>
                        <Link to={`/projects/${project.id}`} className="flex items-center gap-2.5 min-w-0">
                          <div className="h-7 w-7 rounded bg-primary/10 flex items-center justify-center shrink-0">
                            <Icon className="h-3.5 w-3.5 text-primary" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm text-ink-primary truncate">{project.name}</p>
                            <p className="text-xs text-ink-tertiary">{TARGET_LABELS[project.target_type]}</p>
                          </div>
                        </Link>
                      </td>
                      <td className="font-mono text-xs max-w-xs truncate">{project.target_value}</td>
                      <td className="text-xs">{project.finding_count}</td>
                      <td className="text-xs">{formatDate(project.created_at)}</td>
                      <td>
                        {project.last_scan_status ? (
                          <StatusBadge status={project.last_scan_status} />
                        ) : (
                          <span className="text-xs text-ink-disabled">No scans</span>
                        )}
                      </td>
                      <td>
                        <button
                          onClick={() => setPendingDelete(project)}
                          className="opacity-0 group-hover:opacity-100 text-ink-tertiary hover:text-critical transition-all"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modalOpen && (
        <NewProjectModal
          onClose={() => setModalOpen(false)}
          onSubmit={(values) => createMutation.mutate(values)}
          submitting={createMutation.isPending}
        />
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        title={`Delete "${pendingDelete?.name}"?`}
        description="This permanently removes the project along with all its scans, findings, and evidence."
        confirmLabel="Delete"
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && deleteMutation.mutate(pendingDelete.id)}
      />
    </div>
  );
}

function NewProjectModal({
  onClose,
  onSubmit,
  submitting,
}: {
  onClose: () => void;
  onSubmit: (values: { name: string; description?: string; target_type: TargetType; target_value: string }) => void;
  submitting: boolean;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [targetType, setTargetType] = useState<TargetType>("website");
  const [targetValue, setTargetValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const placeholder =
    targetType === "website"
      ? "http://localhost:3000"
      : targetType === "github"
        ? "https://github.com/org/repo"
        : "source-code.zip";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Project name is required.");
      return;
    }
    if (!targetValue.trim()) {
      setError(targetType === "zip" ? "Please provide the ZIP filename." : "Target is required.");
      return;
    }
    setError(null);
    onSubmit({ name: name.trim(), description: description.trim() || undefined, target_type: targetType, target_value: targetValue.trim() });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <form onSubmit={handleSubmit} className="card-raised w-full max-w-md p-6">
        <h3 className="font-medium text-ink-primary mb-4">New project</h3>

        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Project name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Demo Vulnerable App" className="input-field" />
          </div>

          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Description (optional)</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="input-field resize-none" />
          </div>

          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Target type</label>
            <div className="grid grid-cols-3 gap-2">
              {(["website", "github", "zip"] as TargetType[]).map((t) => (
                <button
                  type="button"
                  key={t}
                  onClick={() => setTargetType(t)}
                  className={`text-xs font-medium rounded-md px-2 py-2 border transition-colors ${
                    targetType === t
                      ? "bg-primary/10 border-primary/40 text-primary"
                      : "border-border text-ink-tertiary hover:bg-surface-alt"
                  }`}
                >
                  {TARGET_LABELS[t]}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">
              {targetType === "website" ? "Website URL" : targetType === "github" ? "Repository URL" : "ZIP filename"}
            </label>
            <input value={targetValue} onChange={(e) => setTargetValue(e.target.value)} placeholder={placeholder} className="input-field" />
          </div>

          {error && <p className="text-xs text-critical">{error}</p>}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={submitting} className="btn-primary">
            {submitting ? "Creating…" : "Create project"}
          </button>
        </div>
      </form>
    </div>
  );
}
