import { useMemo, useState } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";
import { listProjects, listScans, listFindingsForScan } from "../services/api";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { SeverityBadge } from "../components/SeverityBadge";
import { StatusBadge } from "../components/StatusBadge";
import { formatConfidence } from "../lib/utils";
import type { FindingDetail, FindingStatus, Severity } from "../types";

const SEVERITY_ORDER: Record<Severity, number> = { critical: 0, high: 1, medium: 2, low: 3, informational: 4 };
type SortKey = "severity" | "confidence" | "newest" | "oldest";

export default function Findings() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: listProjects });

  const scanQueries = useQueries({
    queries: (projects ?? []).map((p) => ({
      queryKey: ["scans", p.id],
      queryFn: () => listScans(p.id),
      enabled: !!projects,
    })),
  });

  const allScans = scanQueries.flatMap((q) => q.data ?? []);
  const scansLoaded = projects !== undefined && scanQueries.every((q) => !q.isLoading);

  const findingQueries = useQueries({
    queries: allScans.map((scan) => ({
      queryKey: ["scan-findings", scan.id],
      queryFn: () => listFindingsForScan(scan.id),
      enabled: scansLoaded,
    })),
  });

  const isLoading = !scansLoaded || findingQueries.some((q) => q.isLoading);
  const allFindings = findingQueries.flatMap((q) => q.data ?? []);

  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [statusFilter, setStatusFilter] = useState<FindingStatus | "all">("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [sortKey, setSortKey] = useState<SortKey>("severity");

  const categories = useMemo(
    () => Array.from(new Set(allFindings.map((f) => f.category))).sort(),
    [allFindings]
  );

  const filtered = useMemo(() => {
    let result = allFindings.filter((f) => {
      if (severityFilter !== "all" && f.severity !== severityFilter) return false;
      if (statusFilter !== "all" && f.status !== statusFilter) return false;
      if (categoryFilter !== "all" && f.category !== categoryFilter) return false;
      return true;
    });

    result = [...result].sort((a, b) => {
      switch (sortKey) {
        case "severity":
          return SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity];
        case "confidence":
          return b.confidence - a.confidence;
        case "newest":
          return b.created_at.localeCompare(a.created_at);
        case "oldest":
          return a.created_at.localeCompare(b.created_at);
        default:
          return 0;
      }
    });

    return result;
  }, [allFindings, severityFilter, statusFilter, categoryFilter, sortKey]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Findings</h1>
        <p className="text-sm text-slate-500 mt-1">Security and code-quality findings across all scans.</p>
      </div>

      {!isLoading && allFindings.length > 0 && (
        <div className="flex flex-wrap gap-3">
          <Select label="Severity" value={severityFilter} onChange={setSeverityFilter} options={["all", "critical", "high", "medium", "low", "informational"]} />
          <Select label="Status" value={statusFilter} onChange={setStatusFilter} options={["all", "potential", "confirmed", "open", "false_positive", "accepted_risk", "resolved"]} />
          <Select label="Category" value={categoryFilter} onChange={setCategoryFilter} options={["all", ...categories]} />
          <Select label="Sort" value={sortKey} onChange={(v) => setSortKey(v as SortKey)} options={["severity", "confidence", "newest", "oldest"]} />
        </div>
      )}

      <div className="card">
        {isLoading ? (
          <div className="p-5 space-y-3">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : allFindings.length === 0 ? (
          <div className="p-5">
            <EmptyState
              icon={ShieldAlert}
              title="No verified findings detected"
              description="Findings are only created from real, evidence-backed analysis — none has run yet."
            />
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-5">
            <EmptyState icon={ShieldAlert} title="No findings match these filters" description="Try adjusting or clearing a filter above." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-500 border-b border-border">
                  <th className="font-medium px-5 py-3">Severity</th>
                  <th className="font-medium px-5 py-3">Finding</th>
                  <th className="font-medium px-5 py-3">Category</th>
                  <th className="font-medium px-5 py-3">Confidence</th>
                  <th className="font-medium px-5 py-3">Location</th>
                  <th className="font-medium px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((f: FindingDetail) => (
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
                    <td className="px-5 py-3 text-slate-500 font-mono text-xs">
                      {f.file ? `${f.file}:${f.start_line ?? "?"}` : f.endpoint ? `${f.http_method ?? "GET"} ${f.endpoint}` : "Location unavailable"}
                    </td>
                    <td className="px-5 py-3">
                      <StatusBadge status={f.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function Select<T extends string>({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: T;
  onChange: (value: T) => void;
  options: string[];
}) {
  return (
    <label className="flex items-center gap-2 text-xs text-slate-500">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="bg-surface-alt border border-border rounded-lg px-2.5 py-1.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-primary/50 capitalize"
      >
        {options.map((o) => (
          <option key={o} value={o} className="capitalize">
            {o === "all" ? `All ${label.toLowerCase()}` : o.replace("_", " ")}
          </option>
        ))}
      </select>
    </label>
  );
}
