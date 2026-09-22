import { cn } from "../lib/utils";
import type { Severity } from "../types";

const STYLES: Record<Severity, string> = {
  critical: "bg-critical/15 text-critical border border-critical/30",
  high: "bg-high/15 text-high border border-high/30",
  medium: "bg-medium/15 text-medium border border-medium/30",
  low: "bg-low/15 text-low border border-low/30",
  informational: "bg-info/15 text-info border border-info/30",
};

const LABELS: Record<Severity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  informational: "Informational",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return <span className={cn("badge", STYLES[severity])}>{LABELS[severity]}</span>;
}
