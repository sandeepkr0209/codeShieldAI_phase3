import { Link, Navigate } from "react-router-dom";
import {
  ArrowRight, Code2, Globe, Radar, Brain, FileSearch, CheckCircle2,
  Wrench, FileText, ShieldCheck, Lock,
} from "lucide-react";
import { PublicNav } from "./PublicNav";
import { PublicFooter } from "./PublicFooter";
import { SeverityBadge } from "../../components/SeverityBadge";
import { StatusBadge } from "../../components/StatusBadge";
import { useAuth } from "../../hooks/useAuth";

const WORKFLOW_STEPS = [
  "Repository / Application", "Application Understanding", "Attack Surface Discovery",
  "Static Analysis", "Dynamic Analysis", "AI Security Reasoning", "Evidence",
  "Verification", "Finding", "Remediation", "Report",
];

const CAPABILITIES = [
  { icon: Code2, title: "Static analysis (SAST)", body: "Analyzes source code with Semgrep and Bandit, structurally parsed via Tree-sitter, to identify potential security issues with real file and line locations — never guessed." },
  { icon: Globe, title: "Dynamic analysis", body: "Inspects a live, authorized application's behavior through controlled, non-destructive HTTP interactions — scoped to same-origin, rate-limited, with fixed request and duration limits." },
  { icon: Radar, title: "Attack surface discovery", body: "Discovers routes, endpoints, parameters, forms, and application components during reconnaissance, building a map of what your application actually exposes." },
  { icon: Brain, title: "AI security reasoning", body: "An explicit Security Agent — one reasoning engine, not a black box — walks Observation → Hypothesis → Test → Evidence → Verification → Conclusion for every finding." },
  { icon: FileSearch, title: "Evidence", body: "Every finding is connected to actual source locations or runtime evidence — the exact file, line, request, or response that led to it." },
  { icon: CheckCircle2, title: "Verification", body: "A deterministic verification layer — never LLM confidence alone — distinguishes raw observations from findings genuinely supported by evidence." },
  { icon: Wrench, title: "Remediation", body: "Findings come with concrete, actionable remediation guidance grounded in retrieved OWASP/CWE security knowledge, not invented by the model." },
  { icon: FileText, title: "Reports", body: "Generate a structured HTML security report — executive summary, findings, evidence, CWE/OWASP mapping, remediation — ready to share with a developer or lead." },
];

export default function Landing() {
  const { isAuthenticated, isLoading } = useAuth();

  // A signed-in user landing on "/" goes straight to the workspace —
  // they don't need the marketing site again. A first-time visitor
  // (unauthenticated) always sees the product site, never a forced login.
  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="bg-background min-h-screen">
      <PublicNav />

      {/* --- Hero --- */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-16">
        <div className="max-w-2xl">
          <span className="badge bg-primary/10 text-primary border border-primary/25 mb-5">
            AI-assisted application security
          </span>
          <h1 className="text-4xl sm:text-5xl font-semibold text-ink-primary tracking-tight leading-[1.1]">
            Find vulnerabilities. Understand the evidence. Fix with confidence.
          </h1>
          <p className="text-ink-secondary text-base mt-5 leading-relaxed max-w-xl">
            CodeShieldAI analyzes your source code and authorized applications, grounds every
            finding in real evidence — not model guesswork — and explains exactly why something
            is a problem and how to fix it.
          </p>
          <div className="flex items-center gap-3 mt-8">
            <Link to="/register" className="btn-primary flex items-center gap-1.5 px-5 py-2.5">
              Get started <ArrowRight className="h-3.5 w-3.5" />
            </Link>
            <a href="#how-it-works" className="btn-secondary px-5 py-2.5">Explore how it works</a>
          </div>
        </div>

        {/* Product preview — illustrative, clearly labeled, not real backend data */}
        <div className="mt-16 card-raised p-1.5 max-w-4xl">
          <div className="rounded-md bg-surface border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-border">
              <span className="text-xs text-ink-tertiary">Findings — Example preview</span>
              <span className="badge bg-surface-alt border border-border text-ink-tertiary">Illustrative, not live data</span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Severity</th><th>Finding</th><th>Location</th><th>Confidence</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><SeverityBadge severity="critical" /></td>
                  <td className="text-ink-primary">SQL Injection</td>
                  <td className="font-mono text-xs">users.py:84</td>
                  <td>94%</td>
                  <td><StatusBadge status="confirmed" /></td>
                </tr>
                <tr>
                  <td><SeverityBadge severity="high" /></td>
                  <td className="text-ink-primary">Broken Access Control</td>
                  <td className="font-mono text-xs">routes.py:142</td>
                  <td>91%</td>
                  <td><StatusBadge status="potential" /></td>
                </tr>
                <tr>
                  <td><SeverityBadge severity="medium" /></td>
                  <td className="text-ink-primary">Missing Security Header</td>
                  <td className="font-mono text-xs">GET /api/users</td>
                  <td>87%</td>
                  <td><StatusBadge status="open" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* --- Workflow --- */}
      <section id="how-it-works" className="max-w-6xl mx-auto px-6 py-16 border-t border-border">
        <h2 className="text-section-title text-ink-primary mb-2">How CodeShieldAI works</h2>
        <p className="text-ink-secondary text-sm mb-8 max-w-2xl">
          Every finding follows the same evidence-driven path — an LLM alone never decides
          something is vulnerable.
        </p>
        <div className="flex flex-wrap gap-2">
          {WORKFLOW_STEPS.map((step, idx) => (
            <div key={step} className="flex items-center gap-2">
              <div className="px-3 py-2 rounded-md border border-border bg-surface text-xs text-ink-secondary whitespace-nowrap">
                {step}
              </div>
              {idx < WORKFLOW_STEPS.length - 1 && <ArrowRight className="h-3 w-3 text-ink-disabled shrink-0" />}
            </div>
          ))}
        </div>
      </section>

      {/* --- Capabilities --- */}
      <section id="product" className="max-w-6xl mx-auto px-6 py-16 border-t border-border">
        <h2 className="text-section-title text-ink-primary mb-2">Capabilities</h2>
        <p className="text-ink-secondary text-sm mb-8 max-w-2xl">
          What's actually implemented today — nothing here is aspirational.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {CAPABILITIES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="card p-5">
              <Icon className="h-4 w-4 text-primary mb-3" />
              <h3 className="text-sm font-medium text-ink-primary mb-1.5">{title}</h3>
              <p className="text-xs text-ink-tertiary leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* --- Trust / why LLM alone isn't enough --- */}
      <section id="security" className="max-w-6xl mx-auto px-6 py-16 border-t border-border">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
          <div>
            <h2 className="text-section-title text-ink-primary mb-3">Why an LLM alone can't determine vulnerabilities reliably</h2>
            <p className="text-sm text-ink-secondary leading-relaxed mb-4">
              A language model asked "is this vulnerable?" will produce a confident-sounding
              answer whether or not it's correct. CodeShieldAI never lets the model make that
              call alone — deterministic tools (Semgrep, Bandit, controlled HTTP checks)
              produce the raw observation, retrieved OWASP/CWE knowledge grounds the
              explanation, and a separate deterministic verification layer decides whether
              the evidence actually supports the conclusion.
            </p>
            <div className="flex items-center gap-2 mt-6">
              <Lock className="h-4 w-4 text-ink-tertiary" />
              <p className="text-xs text-ink-tertiary">
                Scope-controlled by design — dynamic testing is restricted to the target's own
                origin, with fixed request and duration limits the system itself cannot exceed.
              </p>
            </div>
          </div>
          <div className="card p-5">
            <p className="text-xs font-medium text-ink-tertiary uppercase tracking-wide mb-3">What CodeShieldAI is — and isn't</p>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                <p className="text-ink-secondary">An AI-assisted application security analysis platform, grounded in real evidence.</p>
              </div>
              <div className="flex items-start gap-2.5">
                <ShieldCheck className="h-4 w-4 text-ink-tertiary shrink-0 mt-0.5" />
                <p className="text-ink-tertiary">Not an autonomous penetration-testing system, and not a guarantee of complete coverage.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FAQ --- */}
      <section id="faq" className="max-w-6xl mx-auto px-6 py-16 border-t border-border">
        <h2 className="text-section-title text-ink-primary mb-6">Frequently asked questions</h2>
        <div className="max-w-2xl space-y-5">
          {[
            { q: "Does CodeShieldAI guarantee it finds every vulnerability?", a: "No. It covers a defined set of vulnerability classes (SQL injection, XSS, broken access control, security misconfiguration, and more) — see the capabilities above. False negatives are possible, and CodeShieldAI is not a substitute for professional security review." },
            { q: "Is dynamic testing safe to run against my application?", a: "Dynamic checks are non-destructive and scoped to the target's own origin, with fixed page/request/duration limits. Only run it against applications you're authorized to test." },
            { q: "What happens to my source code and scan results?", a: "Projects, scans, findings, and source code belong to your account. Other users cannot access your data — every request is checked against resource ownership on the backend, not just hidden in the UI." },
          ].map(({ q, a }) => (
            <div key={q} className="border-b border-border pb-5">
              <p className="text-sm font-medium text-ink-primary mb-1.5">{q}</p>
              <p className="text-sm text-ink-tertiary leading-relaxed">{a}</p>
            </div>
          ))}
        </div>
      </section>

      <PublicFooter />
    </div>
  );
}
