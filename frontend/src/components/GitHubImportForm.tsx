import { useState, type FormEvent } from "react";
import { Github } from "lucide-react";

interface GitHubImportFormProps {
  onImport: (repoUrl: string) => void;
  importing: boolean;
}

export function GitHubImportForm({ onImport, importing }: GitHubImportFormProps) {
  const [repoUrl, setRepoUrl] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!repoUrl.trim()) return;
    onImport(repoUrl.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
      <div className="relative flex-1">
        <Github className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          className="w-full bg-surface-alt border border-border rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-primary/50"
        />
      </div>
      <button
        type="submit"
        disabled={importing || !repoUrl.trim()}
        className="px-4 py-2 text-sm rounded-lg bg-primary hover:bg-primary-hover text-white transition-colors disabled:opacity-60 shrink-0"
      >
        {importing ? "Importing…" : "Import public repo"}
      </button>
    </form>
  );
}
