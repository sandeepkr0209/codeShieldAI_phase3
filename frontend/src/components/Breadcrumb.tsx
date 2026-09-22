import { Link, useLocation } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const LABELS: Record<string, string> = {
  dashboard: "Overview",
  projects: "Projects",
  scans: "Scans",
  findings: "Findings",
  "attack-surface": "Attack Surface",
  reports: "Reports",
  "knowledge-base": "Knowledge",
  settings: "Settings",
};

/** Path-segment breadcrumb. Dynamic ID segments (uuids) are shown
 * truncated rather than resolved to an entity name — resolving would
 * need an extra fetch per segment, which isn't worth it for a trail
 * that's mostly used for orientation, not navigation. */
export function Breadcrumb() {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav className="flex items-center gap-1.5 text-sm min-w-0">
      {segments.map((seg, idx) => {
        const path = "/" + segments.slice(0, idx + 1).join("/");
        const isLast = idx === segments.length - 1;
        const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}/i.test(seg);
        const label = LABELS[seg] ?? (isUuid ? `${seg.slice(0, 8)}…` : seg);

        return (
          <span key={path} className="flex items-center gap-1.5 min-w-0">
            {idx > 0 && <ChevronRight className="h-3.5 w-3.5 text-ink-disabled shrink-0" />}
            {isLast ? (
              <span className="text-ink-primary font-medium truncate">{label}</span>
            ) : (
              <Link to={path} className="text-ink-tertiary hover:text-ink-primary transition-colors truncate">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
