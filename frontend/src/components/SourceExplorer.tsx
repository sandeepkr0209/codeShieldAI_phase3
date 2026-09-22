import { FileCode, FolderTree } from "lucide-react";
import { EmptyState } from "./EmptyState";
import type { SourceFile } from "../types";

const LANGUAGE_COLORS: Record<string, string> = {
  python: "bg-blue-500",
  javascript: "bg-yellow-400",
  typescript: "bg-sky-500",
  java: "bg-orange-500",
  c: "bg-slate-400",
  cpp: "bg-pink-500",
  csharp: "bg-purple-500",
  go: "bg-cyan-400",
  php: "bg-indigo-400",
};

export function SourceExplorer({ files }: { files: SourceFile[] }) {
  if (files.length === 0) {
    return (
      <EmptyState
        icon={FolderTree}
        title="No source files indexed yet"
        description="Upload a ZIP or import a GitHub repository to see the file breakdown here."
      />
    );
  }

  const languageCounts = files.reduce<Record<string, number>>((acc, f) => {
    const key = f.language ?? "other";
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4">
        {Object.entries(languageCounts).map(([lang, count]) => (
          <span key={lang} className="badge bg-surface-alt border border-border text-slate-300">
            <span className={`h-1.5 w-1.5 rounded-full ${LANGUAGE_COLORS[lang] ?? "bg-slate-500"}`} />
            {lang} · {count}
          </span>
        ))}
      </div>

      <div className="overflow-x-auto -mx-5">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-500 border-b border-border">
              <th className="font-medium px-5 py-2">File</th>
              <th className="font-medium px-5 py-2">Language</th>
              <th className="font-medium px-5 py-2">Functions</th>
              <th className="font-medium px-5 py-2">Classes</th>
              <th className="font-medium px-5 py-2">Size</th>
            </tr>
          </thead>
          <tbody>
            {files.map((f) => (
              <tr key={f.id} className="border-b border-border last:border-0 hover:bg-surface-alt/60">
                <td className="px-5 py-2.5">
                  <span className="flex items-center gap-2 text-slate-200 font-mono text-xs">
                    <FileCode className="h-3.5 w-3.5 text-slate-500 shrink-0" />
                    {f.path}
                  </span>
                </td>
                <td className="px-5 py-2.5 text-slate-400">{f.language ?? "—"}</td>
                <td className="px-5 py-2.5 text-slate-400">{f.function_count}</td>
                <td className="px-5 py-2.5 text-slate-400">{f.class_count}</td>
                <td className="px-5 py-2.5 text-slate-500 text-xs">{(f.size / 1024).toFixed(1)} KB</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
