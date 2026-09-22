import { cn } from "../lib/utils";

const STYLES: Record<string, string> = {
  pending: "bg-info/15 text-info border border-info/30",
  running: "bg-primary/15 text-primary border border-primary/30",
  completed: "bg-success/15 text-success border border-success/30",
  failed: "bg-critical/15 text-critical border border-critical/30",
  potential: "bg-accent/15 text-accent border border-accent/30",
  open: "bg-medium/15 text-medium border border-medium/30",
  confirmed: "bg-critical/15 text-critical border border-critical/30",
  false_positive: "bg-info/15 text-info border border-info/30",
  accepted_risk: "bg-medium/15 text-medium border border-medium/30",
  resolved: "bg-success/15 text-success border border-success/30",
};

export function StatusBadge({ status }: { status: string }) {
  const label = status.replace("_", " ");
  return (
    <span className={cn("badge capitalize", STYLES[status] ?? "bg-slate-700/40 text-slate-300 border border-border")}>
      {label}
    </span>
  );
}
