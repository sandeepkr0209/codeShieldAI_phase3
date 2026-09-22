import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useSearchParams } from "react-router-dom";
import { ShieldCheck, AlertCircle } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { ApiRequestError, googleLoginUrl } from "../services/api";

const OAUTH_ERROR_MESSAGES: Record<string, string> = {
  oauth_state_mismatch: "Google sign-in failed a security check. Please try again.",
  oauth_failed: "Google sign-in failed. Please try again or use email and password.",
  oauth_incomplete_profile: "Google didn't share the information needed to sign you in.",
};

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(
    OAUTH_ERROR_MESSAGES[searchParams.get("error") ?? ""] ?? null
  );
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) {
    const redirectParam = searchParams.get("redirect");
    const fromState = (location.state as { from?: Location })?.from?.pathname;
    const destination = redirectParam ? decodeURIComponent(redirectParam) : fromState ?? "/dashboard";
    return <Navigate to={destination} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Sign in failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <Link to="/" className="h-10 w-10 rounded-lg bg-primary/15 flex items-center justify-center mb-4">
            <ShieldCheck className="h-5 w-5 text-primary" />
          </Link>
          <h1 className="text-lg font-semibold text-ink-primary">Welcome back</h1>
          <p className="text-xs text-ink-tertiary mt-1">Sign in to CodeShieldAI</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {error && (
            <div className="flex items-start gap-2 rounded-md bg-critical/10 border border-critical/30 px-3 py-2.5">
              <AlertCircle className="h-4 w-4 text-critical shrink-0 mt-0.5" />
              <p className="text-xs text-critical">{error}</p>
            </div>
          )}

          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" />
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full py-2.5">
            {submitting ? "Signing in…" : "Sign in"}
          </button>

          <div className="relative py-1">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-[11px]">
              <span className="bg-surface px-2 text-ink-disabled">or</span>
            </div>
          </div>

          <a href={googleLoginUrl()} className="btn-secondary w-full flex items-center justify-center py-2.5">
            Continue with Google
          </a>
        </form>

        <p className="text-center text-sm text-ink-tertiary mt-5">
          Don't have an account?{" "}
          <Link to="/register" className="text-primary hover:text-primary-hover font-medium">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}
