import { useState, type FormEvent } from "react";
import { Link, Navigate } from "react-router-dom";
import { ShieldCheck, AlertCircle, Check, X } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { ApiRequestError, googleLoginUrl } from "../services/api";
import { cn } from "../lib/utils";

const MIN_PASSWORD_LENGTH = 8;

export default function Register() {
  const { register, isAuthenticated } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const passwordLongEnough = password.length >= MIN_PASSWORD_LENGTH;
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!passwordLongEnough) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
      return;
    }
    if (!passwordsMatch) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      await register(name, email, password, confirmPassword);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Registration failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <Link to="/" className="h-10 w-10 rounded-lg bg-primary/15 flex items-center justify-center mb-4">
            <ShieldCheck className="h-5 w-5 text-primary" />
          </Link>
          <h1 className="text-lg font-semibold text-ink-primary">Create your account</h1>
          <p className="text-xs text-ink-tertiary mt-1">Start analyzing your application's security</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {error && (
            <div className="flex items-start gap-2 rounded-md bg-critical/10 border border-critical/30 px-3 py-2.5">
              <AlertCircle className="h-4 w-4 text-critical shrink-0 mt-0.5" />
              <p className="text-xs text-critical">{error}</p>
            </div>
          )}

          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Name</label>
            <input required value={name} onChange={(e) => setName(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" />
            {password.length > 0 && (
              <p className={cn("text-[11px] mt-1.5 flex items-center gap-1", passwordLongEnough ? "text-success" : "text-ink-tertiary")}>
                {passwordLongEnough ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                At least {MIN_PASSWORD_LENGTH} characters
              </p>
            )}
          </div>
          <div>
            <label className="text-xs font-medium text-ink-tertiary block mb-1.5">Confirm password</label>
            <input type="password" required value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="input-field" />
            {confirmPassword.length > 0 && (
              <p className={cn("text-[11px] mt-1.5 flex items-center gap-1", passwordsMatch ? "text-success" : "text-critical")}>
                {passwordsMatch ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                Passwords match
              </p>
            )}
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full py-2.5">
            {submitting ? "Creating account…" : "Create account"}
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
          Already have an account?{" "}
          <Link to="/login" className="text-primary hover:text-primary-hover font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
