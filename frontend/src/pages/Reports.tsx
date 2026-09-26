import { useQueries, useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { FileText, Download } from "lucide-react";
import {
  downloadReportUrl,
  generateReport,
  listProjects,
  listScans,
  listReportsForScan,
} from "../services/api";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { useToast } from "../hooks/useToast";
import { formatDate } from "../lib/utils";

export default function Reports() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: listProjects,
  });

  const scanQueries = useQueries({
    queries: (projects ?? []).map((p) => ({
      queryKey: ["scans", p.id],
      queryFn: () => listScans(p.id),
      enabled: !!projects,
    })),
  });

  const allScans = scanQueries.flatMap((q) => q.data ?? []);

  const scansLoaded =
    projects !== undefined &&
    scanQueries.every((q) => !q.isLoading);

  const completedScans = allScans.filter(
    (s) => s.status === "completed"
  );

  const reportQueries = useQueries({
    queries: allScans.map((scan) => ({
      queryKey: ["reports", scan.id],
      queryFn: () => listReportsForScan(scan.id),
      enabled: scansLoaded,
    })),
  });

  const isLoading =
    !scansLoaded ||
    reportQueries.some((q) => q.isLoading);

  const allReports = reportQueries.flatMap(
    (q) => q.data ?? []
  );

  const scansWithReports = completedScans;

  const generateMutation = useMutation({
    mutationFn: (scanId: string) =>
      generateReport(scanId),

    onSuccess: (_, scanId) => {
      queryClient.invalidateQueries({
        queryKey: ["reports", scanId],
      });

      showToast(
        "Report generated",
        "success"
      );
    },

    onError: (err: Error) =>
      showToast(
        err.message,
        "error"
      ),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">
          Reports
        </h1>

        <p className="text-sm text-slate-500 mt-1">
          Generated HTML security reports for completed scans.
        </p>
      </div>

      {!isLoading &&
        scansWithReports.length > 0 && (
          <div className="card p-5">
            <h3 className="text-sm font-medium text-slate-300 mb-3">
              Completed scans without a report yet
            </h3>

            <div className="divide-y divide-border">
              {scansWithReports.map((scan) => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between py-2.5"
                >
                  <Link
                    to={`/scans/${scan.id}`}
                    className="text-sm text-slate-300 hover:text-primary font-mono"
                  >
                    {scan.id.slice(0, 8)}… —{" "}
                    {scan.scan_type}
                  </Link>

                  <button
                    onClick={() =>
                      generateMutation.mutate(
                        scan.id
                      )
                    }
                    disabled={
                      generateMutation.isPending
                    }
                    className="px-3 py-1.5 text-xs rounded-lg bg-primary hover:bg-primary-hover text-white transition-colors disabled:opacity-60"
                  >
                    Generate
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

      <div className="card p-5">
        {isLoading ? (
          <CardSkeleton />
        ) : allReports.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No reports generated yet"
            description="Generate a report from a completed scan's page, or use the list above."
          />
        ) : (
          <div className="divide-y divide-border">
            {allReports.map((r) => {
              const scan = allScans.find(
                (s) => s.id === r.scan_id
              );

              const reportTitle =
                r.report_name ||
                (scan?.scan_type === "source_code"
                  ? "Source Code Security Report"
                  : scan?.scan_type === "web_application"
                    ? "Web Application Security Report"
                    : "Security Assessment Report");

              return (
                <div
                  key={r.id}
                  className="flex items-center justify-between py-3"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-slate-500" />

                    <div>
                      <Link
                        to={`/scans/${r.scan_id}`}
                        className="text-sm text-slate-200 hover:text-primary"
                      >
                        {reportTitle}
                      </Link>

                      <p className="text-xs text-slate-500 mt-0.5">
                        Scan:{" "}
                        {r.scan_id.slice(0, 8)}
                        … ·{" "}
                        {formatDate(
                          r.created_at
                        )}
                      </p>
                    </div>
                  </div>

                  <a
                    href={downloadReportUrl(r.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-500 hover:text-primary"
                    title="Download report"
                  >
                    <Download className="h-4 w-4" />
                  </a>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}