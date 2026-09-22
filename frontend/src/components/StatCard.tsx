import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "default" | "critical" | "success";
}

export function StatCard({ label, value, icon: Icon, tone = "default" }: StatCardProps) {
  const toneClasses =
    tone === "critical"
      ? "text-critical bg-critical/10"
      : tone === "success"
        ? "text-success bg-success/10"
        : "text-primary bg-primary/10";

  return (
    <div className="card p-4 flex items-center justify-between">
      <div>
        <p className="text-meta font-medium text-ink-tertiary uppercase tracking-wide">{label}</p>
        <p className="text-xl font-semibold text-ink-primary mt-1">{value}</p>
      </div>
      <div className={`h-9 w-9 rounded-md flex items-center justify-center ${toneClasses}`}>
        <Icon className="h-4 w-4" />
      </div>
    </div>
  );
}
