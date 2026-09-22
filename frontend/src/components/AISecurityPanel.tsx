/**
 * Reusable AI analysis panel.
 *
 * Phase 1: presentational only — it communicates what the Security
 * Agent will do once implemented (Phase 4), without performing any
 * autonomous reasoning itself.
 */
import { Sparkles, FileSearch, BookOpen, Gauge } from "lucide-react";

interface AISecurityPanelProps {
  evidenceCount?: number;
  knowledgeRefCount?: number;
  confidence?: number | null;
}

export function AISecurityPanel({
  evidenceCount = 0,
  knowledgeRefCount = 0,
  confidence = null,
}: AISecurityPanelProps) {
  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <Sparkles className="h-4 w-4 text-accent" />
        <h3 className="font-medium text-slate-100">AI Security Analysis</h3>
      </div>
      <p className="text-sm text-slate-500 mb-4">
        CodeShieldAI uses evidence and security knowledge to reason about potential vulnerabilities.
      </p>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-surface-alt border border-border p-3">
          <FileSearch className="h-4 w-4 text-slate-500 mb-1.5" />
          <p className="text-lg font-semibold text-slate-100">{evidenceCount}</p>
          <p className="text-xs text-slate-500">Evidence items</p>
        </div>
        <div className="rounded-lg bg-surface-alt border border-border p-3">
          <BookOpen className="h-4 w-4 text-slate-500 mb-1.5" />
          <p className="text-lg font-semibold text-slate-100">{knowledgeRefCount}</p>
          <p className="text-xs text-slate-500">Knowledge refs</p>
        </div>
        <div className="rounded-lg bg-surface-alt border border-border p-3">
          <Gauge className="h-4 w-4 text-slate-500 mb-1.5" />
          <p className="text-lg font-semibold text-slate-100">
            {confidence !== null ? `${Math.round(confidence * 100)}%` : "—"}
          </p>
          <p className="text-xs text-slate-500">Confidence</p>
        </div>
      </div>

      <p className="text-xs text-slate-600 mt-4 border-t border-border pt-3">
        Reasoning status: <span className="text-slate-400">Security Agent not yet enabled (Phase 4)</span>
      </p>
    </div>
  );
}
