import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";

export function PublicFooter() {
  return (
    <footer className="border-t border-border mt-24">
      <div className="max-w-6xl mx-auto px-6 py-12 grid grid-cols-1 sm:grid-cols-3 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="h-6 w-6 rounded bg-primary/15 flex items-center justify-center">
              <ShieldCheck className="h-3.5 w-3.5 text-primary" />
            </div>
            <span className="text-sm font-semibold text-ink-primary">CodeShieldAI</span>
          </div>
          <p className="text-xs text-ink-tertiary leading-relaxed max-w-xs">
            An AI-assisted application security analysis platform — not an autonomous
            penetration-testing system. Built to help you understand your application's
            security posture, with evidence you can verify yourself.
          </p>
        </div>
        <div>
          <p className="text-xs font-medium text-ink-secondary uppercase tracking-wide mb-3">Product</p>
          <ul className="space-y-2 text-sm text-ink-tertiary">
            <li><a href="#product" className="hover:text-ink-primary transition-colors">Overview</a></li>
            <li><a href="#how-it-works" className="hover:text-ink-primary transition-colors">How it works</a></li>
            <li><a href="#security" className="hover:text-ink-primary transition-colors">Security capabilities</a></li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-medium text-ink-secondary uppercase tracking-wide mb-3">Account</p>
          <ul className="space-y-2 text-sm text-ink-tertiary">
            <li><Link to="/login" className="hover:text-ink-primary transition-colors">Sign in</Link></li>
            <li><Link to="/register" className="hover:text-ink-primary transition-colors">Create account</Link></li>
          </ul>
        </div>
      </div>
      <div className="max-w-6xl mx-auto px-6 py-6 border-t border-border text-xs text-ink-disabled">
        CodeShieldAI — AI-assisted application security analysis. Not a substitute for professional penetration testing.
      </div>
    </footer>
  );
}
