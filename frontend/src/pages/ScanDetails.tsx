import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ScanLine, ArrowLeft, ShieldAlert, Globe, FileText, Download } from "lucide-react";
import {
  generateReport,
  getScan,
  listFindingsForScan,
  listReportsForScan,
  listScanEndpoints,
  listScanPages,
  listScanSourceFiles,
  downloadReportUrl,
} from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import { SeverityBadge } from "../components/SeverityBadge";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { AISecurityPanel } from "../components/AISecurityPanel";
import { AnalysisProgress } from "../components/AnalysisProgress";
import { SourceExplorer } from "../components/SourceExplorer";
import { useToast } from "../hooks/useToast";
import { formatConfidence, formatDate } from "../lib/utils";
import type { FindingDetail } from "../types";

export default function ScanDetails() {
  const { scanId } = useParams<{ scanId: string }>();
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const { data: scan, isLoading: scanLoading } = useQuery({
    queryKey: ["scan", scanId],
    queryFn: () => getScan(scanId!),
    enabled: !!scanId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "running" || status === "pending" ? 2000 : false;
    },
  });

  const isSourceScan = scan?.scan_type === "source_code";
  const isWebScan = scan?.scan_type === "web_application";

  const { data: findings, isLoading: findingsLoading } = useQuery({
    queryKey: ["scan-findings", scanId],
    queryFn: () => listFindingsForScan(scanId!),
    enabled: !!scanId && scan?.status === "completed",
  });

  const { data: sourceFiles } = useQuery({
    queryKey: ["scan-source-files", scanId],
    queryFn: () => listScanSourceFiles(scanId!),
    enabled: !!scanId && isSourceScan,
  });

  const { data: pages } = useQuery({
    queryKey: ["scan-pages", scanId],
    queryFn: () => listScanPages(scanId!),
    enabled: !!scanId && isWebScan && scan?.status === "completed",
  });

  const { data: endpoints } = useQuery({
    queryKey: ["scan-endpoints", scanId],
    queryFn: () => listScanEndpoints(scanId!),
    enabled: !!scanId && isWebScan && scan?.status === "completed",
  });

  const { data: reports } = useQuery({
    queryKey: ["scan-reports", scanId],
    queryFn: () => listReportsForScan(scanId!),
    enabled: !!scanId && scan?.status === "completed",
  });

  const reportMutation = useMutation({
    mutationFn: () => generateReport(scanId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scan-reports", scanId] });
      showToast("Report generated", "success");
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  if (scanLoading) {
    return <CardSkeleton />;
  }

  if (!scan) {
    return <EmptyState icon={ScanLine} title="Scan not found" description="This scan may have been deleted." />;
  }

  return (
    <div className="space-y-6">
      <Link to={`/projects/${scan.project_id}`} className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-300">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to project
      </Link>

      <div className="card p-5">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              {isWebScan ? <Globe className="h-5 w-5 text-primary" /> : <ScanLine className="h-5 w-5 text-primary" />}
            </div>
            <div>
              <p className="text-sm font-medium text-slate-100">
                {isSourceScan ? "Source Code Scan" : "Web Application Scan"}
              </p>
              <p className="text-xs text-slate-500 mt-0.5 font-mono">{scan.id}</p>
            </div>
          </div>
          <StatusBadge status={scan.status} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-5 pt-5 border-t border-border text-sm">
          <div>
            <p className="text-xs text-slate-500 mb-1">Started</p>
            <p className="text-slate-300">{formatDate(scan.started_at)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Completed</p>
            <p className="text-slate-300">{formatDate(scan.completed_at)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Created</p>
            <p className="text-slate-300">{formatDate(scan.created_at)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Findings</p>
            <p className="text-slate-300">{scan.finding_count}</p>
          </div>
        </div>
      </div>

      <AnalysisProgress
        status={scan.status}
        scanType={scan.scan_type}
        currentStage={scan.current_stage}
        errorMessage={scan.error_message}
        warnings={scan.warnings}
        pagesDiscovered={scan.pages_discovered}
        endpointsDiscovered={scan.endpoints_discovered}
        requestsMade={scan.requests_made}
      />

      <AISecurityPanel
        evidenceCount={findings?.reduce((sum, f) => sum + (f.evidence?.length ?? 0), 0) ?? 0}
        knowledgeRefCount={0}
        confidence={findings && findings.length > 0 ? findings[0].confidence : null}
      />

      {isSourceScan && sourceFiles && sourceFiles.length > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Source files analyzed</h3>
          <SourceExplorer files={sourceFiles} />
        </div>
      )}

      {isWebScan && scan.status === "completed" && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Application map</h3>
          {(!pages || pages.length === 0) && (!endpoints || endpoints.length === 0) ? (
            <EmptyState icon={Globe} title="No pages or endpoints discovered" description="Reconnaissance may have been limited — check warnings above." />
          ) : (
            <div className="space-y-5">
              <div>
                <p className="text-xs text-slate-500 mb-2">Pages ({pages?.length ?? 0})</p>
                <div className="overflow-x-auto -mx-5">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-slate-500 border-b border-border">
                        <th className="font-medium px-5 py-2">URL</th>
                        <th className="font-medium px-5 py-2">Status</th>
                        <th className="font-medium px-5 py-2">Forms</th>
                        <th className="font-medium px-5 py-2">Links</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(pages ?? []).map((p) => (
                        <tr key={p.id} className="border-b border-border last:border-0">
                          <td className="px-5 py-2 text-slate-300 font-mono text-xs truncate max-w-xs">{p.url}</td>
                          <td className="px-5 py-2 text-slate-400">{p.status_code ?? "—"}</td>
                          <td className="px-5 py-2 text-slate-400">{p.form_count}</td>
                          <td className="px-5 py-2 text-slate-400">{p.link_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-2">Endpoints ({endpoints?.length ?? 0})</p>
                <div className="overflow-x-auto -mx-5">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-slate-500 border-b border-border">
                        <th className="font-medium px-5 py-2">Method</th>
                        <th className="font-medium px-5 py-2">URL</th>
                        <th className="font-medium px-5 py-2">Parameters</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(endpoints ?? []).map((e) => (
                        <tr key={e.id} className="border-b border-border last:border-0">
                          <td className="px-5 py-2 text-slate-400">{e.method}</td>
                          <td className="px-5 py-2 text-slate-300 font-mono text-xs truncate max-w-xs">{e.url}</td>
                          <td className="px-5 py-2 text-slate-400 text-xs">
                            {(() => {
                              try {
                                const params = JSON.parse(e.parameters_json ?? "[]");
                                return params.length ? params.join(", ") : "—";
                              } catch {
                                return "—";
                              }
                            })()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-4">Findings</h3>
        {scan.status !== "completed" ? (
          <EmptyState
            icon={ShieldAlert}
            title={scan.status === "failed" ? "Scan failed" : "Scan in progress"}
            description={
              scan.status === "failed"
                ? "This scan did not complete — see the error above."
                : "Findings will appear here once analysis finishes."
            }
          />
        ) : findingsLoading ? (
          <CardSkeleton />
        ) : !findings || findings.length === 0 ? (
          <EmptyState
            icon={ShieldAlert}
            title="No verified findings detected"
            description="Analysis did not surface any findings for this scan."
          />
        ) : (
          <FindingsTable findings={findings} />
        )}
      </div>

      {scan.status === "completed" && (
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-1.5">
              <FileText className="h-4 w-4 text-slate-500" />
              <h3 className="text-sm font-medium text-slate-300">Security report</h3>
            </div>
            <button
              onClick={() => reportMutation.mutate()}
              disabled={reportMutation.isPending}
              className="px-3 py-1.5 text-sm rounded-lg bg-primary hover:bg-primary-hover text-white transition-colors disabled:opacity-60"
            >
              {reportMutation.isPending ? "Generating…" : "Generate report"}
            </button>
          </div>
          {!reports || reports.length === 0 ? (
            <p className="text-xs text-slate-500">No report generated yet for this scan.</p>
          ) : (
            <div className="divide-y divide-border">
              {reports.map((r) => (
                <div key={r.id} className="flex items-center justify-between py-2">
                  <span className="text-sm text-slate-300 uppercase">{r.report_type} report — {formatDate(r.created_at)}</span>
                  <a href={downloadReportUrl(r.id)} target="_blank" rel="noreferrer" className="text-slate-500 hover:text-primary">
                    <Download className="h-4 w-4" />
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function FindingsTable({ findings }: { findings: FindingDetail[] }) {
  return (
    <div className="overflow-x-auto -mx-5">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-slate-500 border-b border-border">
            <th className="font-medium px-5 py-2">Severity</th>
            <th className="font-medium px-5 py-2">Finding</th>
            <th className="font-medium px-5 py-2">Category</th>
            <th className="font-medium px-5 py-2">Confidence</th>
            <th className="font-medium px-5 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <tr key={f.id} className="border-b border-border last:border-0 hover:bg-surface-alt/60">
              <td className="px-5 py-3">
                <SeverityBadge severity={f.severity} />
              </td>
              <td className="px-5 py-3">
                <Link to={`/findings/${f.id}`} className="text-slate-200 hover:text-primary">
                  {f.title}
                </Link>
              </td>
              <td className="px-5 py-3 text-slate-400">{f.category}</td>
              <td className="px-5 py-3 text-slate-400">{formatConfidence(f.confidence)}</td>
              <td className="px-5 py-3">
                <StatusBadge status={f.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
