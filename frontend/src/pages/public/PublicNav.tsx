import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";

export function PublicNav() {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="h-7 w-7 rounded bg-primary/15 flex items-center justify-center">
            <ShieldCheck className="h-4 w-4 text-primary" />
          </div>
          <span className="text-[15px] font-semibold text-ink-primary tracking-tight">CodeShieldAI</span>
        </Link>

        <nav className="hidden md:flex items-center gap-7 text-sm text-ink-secondary">
          <a href="#product" className="hover:text-ink-primary transition-colors">Product</a>
          <a href="#how-it-works" className="hover:text-ink-primary transition-colors">How it works</a>
          <a href="#security" className="hover:text-ink-primary transition-colors">Security</a>
          <a href="#faq" className="hover:text-ink-primary transition-colors">FAQ</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-ghost">Sign in</Link>
          <Link to="/register" className="btn-primary">Get started</Link>
        </div>
      </div>
    </header>
  );
}
