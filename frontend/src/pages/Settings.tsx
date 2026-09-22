import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Database, Sparkles, ShieldCheck, CheckCircle2, XCircle, User as UserIcon, KeyRound } from "lucide-react";
import { changePassword, getHealth, testAI } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { formatDate } from "../lib/utils";

export default function Settings() {
  const { user } = useAuth();
  const { data: health, isLoading } = useQuery({ queryKey: ["health"], queryFn: getHealth });
  const { showToast } = useToast();
  const [prompt, setPrompt] = useState("Say hello and confirm the Groq connection is working.");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const changePasswordMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      showToast("Password updated", "success");
      setCurrentPassword("");
      setNewPassword("");
    },
    onError: (err: Error) => showToast(err.message, "error"),
  });

  const aiTestMutation = useMutation({
    mutationFn: testAI,
    onError: (err: Error) => showToast(err.message, "error"),
  });

  const dbOk = health?.database === "ok";

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Your profile and application status.</p>
      </div>

      <div className="card p-5">
        <div className="flex items-center gap-1.5 mb-4">
          <UserIcon className="h-4 w-4 text-slate-500" />
          <h3 className="text-sm font-medium text-slate-300">Profile</h3>
        </div>
        <div className="flex items-center gap-4">
          {user?.profile_image ? (
            <img src={user.profile_image} alt="" className="h-14 w-14 rounded-xl object-cover" />
          ) : (
            <div className="h-14 w-14 rounded-xl bg-primary/15 flex items-center justify-center text-primary font-medium text-lg">
              {user?.name?.[0]?.toUpperCase() ?? "?"}
            </div>
          )}
          <div>
            <p className="text-sm font-medium text-slate-100">{user?.name}</p>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-5 pt-5 border-t border-border text-sm">
          <div>
            <p className="text-xs text-slate-500 mb-1">Sign-in method</p>
            <p className="text-slate-300 capitalize">{user?.auth_provider}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Member since</p>
            <p className="text-slate-300">{user ? formatDate(user.created_at) : "—"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Last login</p>
            <p className="text-slate-300">{user?.last_login ? formatDate(user.last_login) : "—"}</p>
          </div>
        </div>
      </div>

      {user?.auth_provider === "password" && (
        <div className="card p-5">
          <div className="flex items-center gap-1.5 mb-4">
            <KeyRound className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-medium text-slate-300">Change password</h3>
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              changePasswordMutation.mutate({ current_password: currentPassword, new_password: newPassword });
            }}
            className="space-y-3"
          >
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1.5">Current password</label>
              <input
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full bg-surface-alt border border-border rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-primary/50"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1.5">New password</label>
              <input
                type="password"
                required
                minLength={8}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full bg-surface-alt border border-border rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-primary/50"
              />
            </div>
            <button
              type="submit"
              disabled={changePasswordMutation.isPending}
              className="px-4 py-2 text-sm rounded-lg bg-primary hover:bg-primary-hover text-white transition-colors disabled:opacity-60"
            >
              {changePasswordMutation.isPending ? "Updating…" : "Update password"}
            </button>
          </form>
        </div>
      )}

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-4">System status</h3>
        <div className="space-y-3">
          <StatusRow
            icon={Database}
            label="Database connection"
            ok={isLoading ? null : dbOk}
            detail={isLoading ? "Checking…" : dbOk ? "PostgreSQL reachable" : "Unreachable"}
          />
          <StatusRow
            icon={Sparkles}
            label="LLM configuration (Groq)"
            ok={null}
            detail="Configured via GROQ_API_KEY — use the AI test endpoint to verify a live call"
          />
          <StatusRow
            icon={ShieldCheck}
            label="Security testing scope"
            ok={true}
            detail="Authorized-target-only dynamic testing enforced"
          />
        </div>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-3">AI integration test</h3>
        <p className="text-xs text-slate-500 mb-3">
          Sends a prompt straight to the configured Groq model via the backend's LLMProvider abstraction — this only
          validates connectivity, it is not the Security Agent.
        </p>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="flex-1 bg-surface-alt border border-border rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-primary/50"
          />
          <button
            onClick={() => aiTestMutation.mutate(prompt)}
            disabled={aiTestMutation.isPending || !prompt.trim()}
            className="px-4 py-2 text-sm rounded-lg bg-primary hover:bg-primary-hover text-white transition-colors disabled:opacity-60 shrink-0"
          >
            {aiTestMutation.isPending ? "Sending…" : "Test connection"}
          </button>
        </div>
        {aiTestMutation.data && (
          <div className="mt-3 rounded-lg border border-border bg-surface-alt p-3">
            <p className="text-xs text-slate-500 mb-1">Response from {aiTestMutation.data.model}</p>
            <p className="text-sm text-slate-300 whitespace-pre-wrap">{aiTestMutation.data.response}</p>
          </div>
        )}
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Application preferences</h3>
        <p className="text-xs text-slate-500">
          Preferences and per-user settings will be added as the platform grows beyond Phase 1. Nothing here is
          persisted yet.
        </p>
      </div>

      <div className="card p-5">
        <h3 className="text-sm font-medium text-slate-300 mb-2">Secrets</h3>
        <p className="text-xs text-slate-500">
          API keys (e.g. <code className="text-slate-400">GROQ_API_KEY</code>) are read from environment variables on
          the backend and are never sent to or displayed in this interface.
        </p>
      </div>
    </div>
  );
}

function StatusRow({
  icon: Icon,
  label,
  ok,
  detail,
}: {
  icon: typeof Database;
  label: string;
  ok: boolean | null;
  detail: string;
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <Icon className="h-4 w-4 text-slate-500" />
        <div>
          <p className="text-sm text-slate-200">{label}</p>
          <p className="text-xs text-slate-500">{detail}</p>
        </div>
      </div>
      {ok === null ? (
        <span className="text-xs text-slate-600">—</span>
      ) : ok ? (
        <CheckCircle2 className="h-4 w-4 text-success" />
      ) : (
        <XCircle className="h-4 w-4 text-critical" />
      )}
    </div>
  );
}
