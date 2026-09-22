import { useQuery } from "@tanstack/react-query";
import { BookOpen, Database, Layers } from "lucide-react";
import { getKnowledgeStats } from "../services/api";
import { StatCard } from "../components/StatCard";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";

const PLANNED_SOURCES = ["OWASP Top 10", "OWASP API Security Top 10", "CWE", "CAPEC", "Secure Coding Guidance"];

export default function KnowledgeBase() {
  const { data: stats, isLoading } = useQuery({ queryKey: ["knowledge-stats"], queryFn: getKnowledgeStats });

  const indexedTitles = new Set((stats?.documents ?? []).map((d) => d.toLowerCase()));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Knowledge Base</h1>
        <p className="text-sm text-slate-500 mt-1">
          Security knowledge that powers RAG-based explanations and remediation guidance.
        </p>
      </div>

      {isLoading ? (
        <CardSkeleton />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <StatCard label="Indexed chunks" value={stats?.indexed_chunks ?? 0} icon={Layers} />
          <StatCard label="Documents" value={stats?.documents.length ?? 0} icon={Database} />
        </div>
      )}

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-4">Knowledge sources (initial scope)</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {PLANNED_SOURCES.map((s) => {
            const isIndexed = [...indexedTitles].some((title) => title.includes(s.split(" ")[0].toLowerCase()));
            return (
              <div key={s} className="flex items-center gap-3 rounded-lg border border-border bg-surface-alt px-4 py-3">
                <BookOpen className="h-4 w-4 text-slate-500" />
                <div>
                  <p className="text-sm text-slate-200">{s}</p>
                  <p className="text-xs text-slate-500">{isIndexed ? "Indexed" : "Not yet ingested"}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {!isLoading && (stats?.documents.length ?? 0) === 0 && (
        <div className="card">
          <EmptyState
            icon={Database}
            title="Knowledge base not yet ingested"
            description="Run: python -m app.services.rag.ingestion (from backend/) to index the initial OWASP/CWE knowledge documents."
          />
        </div>
      )}

      {!isLoading && (stats?.documents.length ?? 0) > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Indexed documents</h3>
          <div className="flex flex-wrap gap-2">
            {stats!.documents.map((doc) => (
              <span key={doc} className="badge bg-surface-alt border border-border text-slate-300">
                {doc}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
