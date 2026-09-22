import { useState } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { Radar, Globe } from "lucide-react";
import { listProjects, listScanEndpoints, listScanPages, listScans } from "../services/api";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { Drawer } from "../components/Drawer";
import type { Endpoint } from "../types";

function safePathname(url: string): string {
  try {
    return new URL(url).pathname;
  } catch {
    return url;
  }
}

export default function AttackSurface() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: listProjects });

  const scanQueries = useQueries({
    queries: (projects ?? []).map((p) => ({
      queryKey: ["scans", p.id],
      queryFn: () => listScans(p.id),
      enabled: !!projects,
    })),
  });
  const scansLoaded = projects !== undefined && scanQueries.every((q) => !q.isLoading);
  const webScans = scanQueries
    .flatMap((q) => q.data ?? [])
    .filter((s) => s.scan_type === "web_application" && s.status === "completed");

  const endpointQueries = useQueries({
    queries: webScans.map((scan) => ({
      queryKey: ["scan-endpoints", scan.id],
      queryFn: () => listScanEndpoints(scan.id),
      enabled: scansLoaded,
    })),
  });
  const pageQueries = useQueries({
    queries: webScans.map((scan) => ({
      queryKey: ["scan-pages", scan.id],
      queryFn: () => listScanPages(scan.id),
      enabled: scansLoaded,
    })),
  });

  const isLoading = !scansLoaded || endpointQueries.some((q) => q.isLoading);
  const allEndpoints = endpointQueries.flatMap((q) => q.data ?? []);
  const totalPages = pageQueries.reduce((sum, q) => sum + (q.data?.length ?? 0), 0);

  const [selected, setSelected] = useState<Endpoint | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-page-title text-ink-primary">Attack Surface</h1>
        <p className="text-sm text-ink-tertiary mt-1">
          Pages, routes, and API endpoints discovered across your web application scans.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <div className="card p-4">
          <p className="text-meta text-ink-tertiary uppercase">Web scans</p>
          <p className="text-xl font-semibold text-ink-primary mt-1">{webScans.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-meta text-ink-tertiary uppercase">Pages discovered</p>
          <p className="text-xl font-semibold text-ink-primary mt-1">{totalPages}</p>
        </div>
        <div className="card p-4">
          <p className="text-meta text-ink-tertiary uppercase">Endpoints discovered</p>
          <p className="text-xl font-semibold text-ink-primary mt-1">{allEndpoints.length}</p>
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="p-5"><CardSkeleton /></div>
        ) : allEndpoints.length === 0 ? (
          <div className="p-5">
            <EmptyState
              icon={Radar}
              title="No attack surface discovered yet"
              description="Run a web application scan on a project to discover pages, forms, and endpoints here."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Method</th>
                  <th>URL</th>
                  <th>Parameters</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {allEndpoints.map((e) => {
                  let params: string[] = [];
                  try {
                    params = JSON.parse(e.parameters_json ?? "[]");
                  } catch {
                    params = [];
                  }
                  return (
                    <tr key={e.id} onClick={() => setSelected(e)} className="cursor-pointer">
                      <td className="font-mono text-xs text-ink-secondary">{e.method}</td>
                      <td className="font-mono text-xs text-ink-primary truncate max-w-md">{e.url}</td>
                      <td className="text-xs">{params.length ? params.join(", ") : "—"}</td>
                      <td className="text-xs capitalize">{e.source}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Drawer
        open={!!selected}
        onClose={() => setSelected(null)}
        title={selected ? `${selected.method} ${safePathname(selected.url)}` : ""}
        subtitle={selected?.url}
      >
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Globe className="h-3.5 w-3.5 text-ink-tertiary" />
              <span className="text-xs text-ink-tertiary capitalize">Discovered via {selected.source}</span>
            </div>
            <div>
              <p className="text-xs font-medium text-ink-tertiary uppercase mb-1.5">Parameters</p>
              <p className="text-sm text-ink-secondary font-mono">
                {(() => {
                  try {
                    const p = JSON.parse(selected.parameters_json ?? "[]");
                    return p.length ? p.join(", ") : "None observed";
                  } catch {
                    return "None observed";
                  }
                })()}
              </p>
            </div>
            {selected.response_headers_json && (
              <div>
                <p className="text-xs font-medium text-ink-tertiary uppercase mb-1.5">Response headers</p>
                <pre className="text-xs text-ink-secondary font-mono bg-surface-alt border border-border rounded-md p-3 overflow-x-auto">
                  {selected.response_headers_json}
                </pre>
              </div>
            )}
            {selected.cookies_json && (
              <div>
                <p className="text-xs font-medium text-ink-tertiary uppercase mb-1.5">Cookie names</p>
                <p className="text-sm text-ink-secondary font-mono">{selected.cookies_json}</p>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}
