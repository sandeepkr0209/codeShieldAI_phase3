import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ScanLine, Plus, Globe, Github, FileArchive } from "lucide-react";
import {
  createScan,
  getProject,
  importGithubRepo,
  listProjectSourceFiles,
  listScans,
  uploadSourceZip,
} from "../services/api";
import type { ScanType, TargetType } from "../types";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { SourceUpload } from "../components/SourceUpload";
import { GitHubImportForm } from "../components/GitHubImportForm";
import { SourceExplorer } from "../components/SourceExplorer";
import { useToast } from "../hooks/useToast";
import { formatDate } from "../lib/utils";

const TARGET_ICONS: Record<TargetType, typeof Globe> = {
  website: Globe,
  github: Github,
  zip: FileArchive,
};

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => getProject(projectId!),
    enabled: !!projectId,
  });

  const { data: scans, isLoading: scansLoading } = useQuery({
    queryKey: ["scans", projectId],
    queryFn: () => listScans(projectId!),
    enabled: !!projectId,
  });

  const { data: sourceFiles, isLoading: sourceFilesLoading } = useQuery({
    queryKey: ["project-source-files", projectId],
    queryFn: () => listProjectSourceFiles(projectId!),
    enabled: !!projectId,
  });

  const scanMutation = useMutation({
    mutationFn: (scanType: ScanType) => createScan(projectId!, scanType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scans", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      showToast("Scan started — track progress on the scan page", "success");
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadSourceZip(projectId!, file),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["project-source-files", projectId] });
      showToast(`Ingested ${result.files_ingested} files`, "success");
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  const importMutation = useMutation({
    mutationFn: (repoUrl: string) => importGithubRepo(projectId!, repoUrl),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["project-source-files", projectId] });
      showToast(`Imported ${result.files_ingested} files from GitHub`, "success");
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  if (projectLoading) return <CardSkeleton />;
  if (!project) {
    return <EmptyState icon={ScanLine} title="Project not found" description="This project may have been deleted." />;
  }

  const Icon = TARGET_ICONS[project.target_type];
  const defaultScanType: ScanType = project.target_type === "website" ? "web_application" : "source_code";
  const hasSource = (sourceFiles?.length ?? 0) > 0;

  return (
    <div className="space-y-6">
      <Link to="/projects" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-300">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to projects
      </Link>

      <div className="card p-5">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-100">{project.name}</p>
              <p className="text-xs text-slate-500 mt-0.5">{project.target_value}</p>
            </div>
          </div>
          <button
            onClick={() => scanMutation.mutate(defaultScanType)}
            disabled={scanMutation.isPending || (defaultScanType === "source_code" && !hasSource)}
            title={defaultScanType === "source_code" && !hasSource ? "Upload or import source code first" : undefined}
            className="flex items-center gap-2 bg-primary hover:bg-primary-hover text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-60"
          >
            <Plus className="h-4 w-4" />
            {scanMutation.isPending ? "Starting…" : "New Scan"}
          </button>
        </div>
        {project.description && <p className="text-sm text-slate-400 mt-4">{project.description}</p>}
        <p className="text-xs text-slate-600 mt-4">Created {formatDate(project.created_at)}</p>
      </div>

      {defaultScanType === "source_code" && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Source code</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
            <SourceUpload onUpload={(file) => uploadMutation.mutate(file)} uploading={uploadMutation.isPending} />
            <div className="rounded-xl border border-border p-5 flex flex-col justify-center">
              <p className="text-xs text-slate-500 mb-3">Or import a public GitHub repository:</p>
              <GitHubImportForm
                onImport={(url) => importMutation.mutate(url)}
                importing={importMutation.isPending}
              />
            </div>
          </div>

          {sourceFilesLoading ? (
            <CardSkeleton />
          ) : (
            <SourceExplorer files={sourceFiles ?? []} />
          )}
        </div>
      )}

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-4">Scan history</h3>
        {scansLoading ? (
          <CardSkeleton />
        ) : !scans || scans.length === 0 ? (
          <EmptyState
            icon={ScanLine}
            title="No scans yet"
            description={
              defaultScanType === "source_code"
                ? "Upload source code above, then start a scan to run static analysis and AI-assisted explanation."
                : "Start a scan to create a scan record. Web application scanning arrives in Phase 5."
            }
          />
        ) : (
          <div className="divide-y divide-border">
            {scans.map((scan) => (
              <Link
                key={scan.id}
                to={`/scans/${scan.id}`}
                className="flex items-center justify-between py-3 hover:bg-surface-alt/50 -mx-5 px-5 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <ScanLine className="h-4 w-4 text-slate-500" />
                  <div>
                    <p className="text-sm text-slate-200">
                      {scan.scan_type === "source_code" ? "Source Code Scan" : "Web Application Scan"}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">{formatDate(scan.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-slate-500">{scan.finding_count} findings</span>
                  <StatusBadge status={scan.status} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
