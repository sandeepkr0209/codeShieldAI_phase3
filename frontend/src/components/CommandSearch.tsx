import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search, FolderKanban } from "lucide-react";
import { listProjects } from "../services/api";

/**
 * Lightweight search: matches project name/target against the
 * already-cached project list (no extra network round trip if the
 * user has already loaded Projects/Dashboard this session).
 * Scoped to projects only — deliberately not pretending to search
 * findings/scans/files without real indexed data behind it.
 */
export function CommandSearch() {
  const navigate = useNavigate();
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: listProjects });
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const matches =
    query.trim().length > 0
      ? (projects ?? []).filter(
          (p) =>
            p.name.toLowerCase().includes(query.toLowerCase()) ||
            p.target_value.toLowerCase().includes(query.toLowerCase())
        )
      : [];

  return (
    <div className="relative w-80 max-w-full" ref={containerRef}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-ink-tertiary" />
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder="Search projects…"
        className="w-full bg-surface-alt border border-border rounded-md pl-8 pr-3 py-1.5 text-sm text-ink-primary placeholder:text-ink-disabled focus:outline-none focus:ring-1 focus:ring-primary/50"
      />
      {open && query.trim().length > 0 && (
        <div className="absolute left-0 right-0 mt-1.5 card-raised shadow-popover py-1 z-30 max-h-72 overflow-y-auto">
          {matches.length === 0 ? (
            <p className="px-3 py-2 text-xs text-ink-tertiary">No matching projects</p>
          ) : (
            matches.map((p) => (
              <button
                key={p.id}
                onClick={() => {
                  navigate(`/projects/${p.id}`);
                  setOpen(false);
                  setQuery("");
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-left hover:bg-surface-alt transition-colors"
              >
                <FolderKanban className="h-3.5 w-3.5 text-ink-tertiary shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm text-ink-primary truncate">{p.name}</p>
                  <p className="text-xs text-ink-tertiary truncate">{p.target_value}</p>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
