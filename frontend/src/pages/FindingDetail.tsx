import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft, ShieldAlert, FileCode2, BookOpen, Globe, Brain,
  AlertTriangle, Wrench, Link2, CheckCircle2, XCircle,
} from "lucide-react";
import { getFinding, listFindingsForScan } from "../services/api";
import { SeverityBadge } from "../components/SeverityBadge";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState } from "../components/EmptyState";
import { CardSkeleton } from "../components/Skeleton";
import { formatConfidence, formatDate } from "../lib/utils";

export default function FindingDetail() {
  const { findingId } = useParams<{ findingId: string }>();

  const { data: finding, isLoading } = useQuery({
    queryKey: ["finding", findingId],
    queryFn: () => getFinding(findingId!),
    enabled: !!findingId,
  });

  const { data: relatedFindings } = useQuery({
    queryKey: ["scan-findings", finding?.scan_id],
    queryFn: () => listFindingsForScan(finding!.scan_id),
    enabled: !!finding?.scan_id,
  });

  if (isLoading) return <CardSkeleton />;
  if (!finding) {
    return <EmptyState icon={ShieldAlert} title="Finding not found" description="This finding may have been removed." />;
  }

  const isDynamic = !!finding.endpoint;
  const staticEvidence = finding.evidence.filter((e) => e.evidence_type === "static_analysis");
  const dynamicEvidence = finding.evidence.filter((e) => e.evidence_type === "dynamic_analysis");
  const knowledgeEvidence = finding.evidence.filter((e) => e.evidence_type === "security_knowledge");

  let reasoningSteps: { label: string; text: string }[] = [];
  try {
    reasoningSteps = finding.reasoning_steps ? JSON.parse(finding.reasoning_steps) : [];
  } catch {
    reasoningSteps = [];
  }

  const related = (relatedFindings ?? []).filter((f) => f.id !== finding.id).slice(0, 5);

  return (
    <div className="space-y-6">
      <Link to="/findings" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-300">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to findings
      </Link>

      {/* --- Finding Overview --- */}
      <div className="card p-5">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <SeverityBadge severity={finding.severity} />
              <StatusBadge status={finding.status} />
              {finding.verified ? (
                <span className="badge bg-success/15 text-success border border-success/30">
                  <CheckCircle2 className="h-3 w-3" /> Verified
                </span>
              ) : (
                <span className="badge bg-slate-700/30 text-slate-400 border border-border">
                  <XCircle className="h-3 w-3" /> Not verified
                </span>
              )}
            </div>
            <h1 className="text-lg font-semibold text-slate-100">{finding.title}</h1>
            <p className="text-sm text-slate-500 mt-1">{finding.category}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-500">Confidence</p>
            <p className="text-lg font-semibold text-slate-100">{formatConfidence(finding.confidence)}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-5 pt-5 border-t border-border text-sm">
          <div>
            <p className="text-xs text-slate-500 mb-1">CWE</p>
            <p className="text-slate-300">{finding.cwe_id ?? "Not mapped"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">OWASP</p>
            <p className="text-slate-300">{finding.owasp_category ?? "Not mapped"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Analyzer</p>
            <p className="text-slate-300 capitalize">{finding.analyzer ?? "—"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Found</p>
            <p className="text-slate-300">{formatDate(finding.created_at)}</p>
          </div>
        </div>
      </div>

      {/* --- Why This Was Detected --- */}
      {finding.description && (
        <div className="card p-5">
          <div className="flex items-center gap-1.5 mb-2">
            <AlertTriangle className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-medium text-slate-300">Why This Was Detected</h3>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{finding.description}</p>
        </div>
      )}

      {/* --- Source Location / Endpoint --- */}
      <div className="card p-5">
        <div className="flex items-center gap-1.5 mb-3">
          {isDynamic ? <Globe className="h-4 w-4 text-slate-500" /> : <FileCode2 className="h-4 w-4 text-slate-500" />}
          <h3 className="text-sm font-medium text-slate-300">{isDynamic ? "Endpoint" : "Source Location"}</h3>
        </div>
        {isDynamic ? (
          <div className="text-sm">
            <p className="text-slate-200 font-mono">{finding.http_method ?? "GET"} {finding.endpoint}</p>
            {finding.parameter && <p className="text-xs text-slate-500 mt-1">Parameter: {finding.parameter}</p>}
          </div>
        ) : finding.file ? (
          <div>
            <p className="text-sm text-slate-200 font-mono">{finding.file}</p>
            <p className="text-xs text-slate-500 mt-1">
              {finding.start_line
                ? `Lines ${finding.start_line}${finding.end_line && finding.end_line !== finding.start_line ? `–${finding.end_line}` : ""}`
                : "Location unavailable"}
            </p>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Location unavailable</p>
        )}
        {finding.code_snippet && (
          <pre className="mt-3 p-3 rounded-lg bg-surface-alt border border-border text-xs text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap">
            {finding.start_line && <span className="text-slate-600 select-none">{finding.start_line}  </span>}
            {finding.code_snippet}
          </pre>
        )}
      </div>

      {/* --- Evidence --- */}
      <div className="card p-5">
        <div className="flex items-center gap-1.5 mb-4">
          <FileCode2 className="h-4 w-4 text-slate-500" />
          <h3 className="text-sm font-medium text-slate-300">Evidence</h3>
        </div>
        {staticEvidence.length === 0 && dynamicEvidence.length === 0 ? (
          <EmptyState icon={FileCode2} title="No evidence recorded" description="This finding has no linked evidence yet." />
        ) : (
          <div className="space-y-3">
            {[...staticEvidence, ...dynamicEvidence].map((ev) => (
              <div key={ev.id} className="rounded-lg border border-border bg-surface-alt">
                <div className="flex items-center justify-between px-4 py-2 border-b border-border">
                  <span className="text-xs font-medium text-slate-400">{ev.evidence_type.replace("_", " ")}</span>
                  {ev.source && <span className="text-xs text-slate-600">{ev.source}</span>}
                </div>
                <pre className="p-4 text-xs text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap">{ev.content}</pre>
              </div>
            ))}
          </div>
        )}
        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-border text-sm">
          <div>
            <p className="text-xs text-slate-500 mb-1">Rule</p>
            <p className="text-slate-300 font-mono text-xs">{finding.rule_id ?? "—"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Verification method</p>
            <p className="text-slate-300">{finding.verification_method ?? "—"}</p>
          </div>
        </div>
        {finding.verification_reason && (
          <p className="text-xs text-slate-400 mt-3 leading-relaxed">{finding.verification_reason}</p>
        )}
      </div>

      {/* --- Request / Response (dynamic findings only) --- */}
      {isDynamic && dynamicEvidence.length > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-slate-300 mb-3">Request / Response</h3>
          <p className="text-xs text-slate-500 mb-3">
            Sanitized — sensitive headers (Authorization, Cookie) are always redacted before storage.
          </p>
          {dynamicEvidence.map((ev) => (
            <pre key={ev.id} className="p-3 rounded-lg bg-surface-alt border border-border text-xs text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap">
              {ev.content}
            </pre>
          ))}
        </div>
      )}

      {/* --- AI Security Reasoning --- */}
      {reasoningSteps.length > 0 && (
        <div className="card p-5">
          <div className="flex items-center gap-1.5 mb-4">
            <Brain className="h-4 w-4 text-accent" />
            <h3 className="text-sm font-medium text-slate-300">AI Security Reasoning</h3>
          </div>
          <div className="space-y-0">
            {reasoningSteps.map((step, idx) => (
              <div key={step.label} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="h-6 w-6 rounded-full bg-primary/15 border border-primary/30 flex items-center justify-center text-[10px] text-primary font-medium shrink-0">
                    {idx + 1}
                  </div>
                  {idx < reasoningSteps.length - 1 && <div className="w-px flex-1 bg-border my-1" />}
                </div>
                <div className="pb-4">
                  <p className="text-xs font-medium text-slate-300">{step.label}</p>
                  <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{step.text || "—"}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* --- Impact --- */}
      {finding.impact && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-slate-300 mb-2">Impact</h3>
          <p className="text-sm text-slate-400 leading-relaxed">{finding.impact}</p>
        </div>
      )}

      {/* --- Remediation --- */}
      {finding.recommendation && (
        <div className="card p-5">
          <div className="flex items-center gap-1.5 mb-2">
            <Wrench className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-medium text-slate-300">Remediation</h3>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed">{finding.recommendation}</p>
        </div>
      )}

      {/* --- Security Knowledge --- */}
      {knowledgeEvidence.length > 0 && (
        <div className="card p-5">
          <div className="flex items-center gap-1.5 mb-1">
            <BookOpen className="h-4 w-4 text-accent" />
            <h3 className="text-sm font-medium text-slate-300">Security Knowledge</h3>
          </div>
          <p className="text-xs text-slate-500 mb-4">
            OWASP/CWE reference material retrieved via RAG and used to support this explanation.
          </p>
          <div className="space-y-3">
            {knowledgeEvidence.map((ev) => (
              <div key={ev.id} className="rounded-lg border border-border bg-surface-alt p-4">
                <p className="text-xs font-medium text-accent mb-1.5">{ev.source}</p>
                <p className="text-xs text-slate-400 whitespace-pre-wrap leading-relaxed">{ev.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* --- Related Findings --- */}
      {related.length > 0 && (
        <div className="card p-5">
          <div className="flex items-center gap-1.5 mb-3">
            <Link2 className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-medium text-slate-300">Related Findings</h3>
          </div>
          <p className="text-xs text-slate-500 mb-3">Other findings from the same scan.</p>
          <div className="divide-y divide-border">
            {related.map((f) => (
              <Link
                key={f.id}
                to={`/findings/${f.id}`}
                className="flex items-center justify-between py-2.5 hover:bg-surface-alt/50 -mx-2 px-2 rounded transition-colors"
              >
                <span className="text-sm text-slate-300 truncate">{f.title}</span>
                <SeverityBadge severity={f.severity} />
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
