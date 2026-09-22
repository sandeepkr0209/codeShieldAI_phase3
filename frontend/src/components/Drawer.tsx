import { X } from "lucide-react";
import type { ReactNode } from "react";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function Drawer({ open, onClose, title, subtitle, children }: DrawerProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-md h-full bg-surface border-l border-border shadow-popover overflow-y-auto">
        <div className="sticky top-0 bg-surface border-b border-border px-5 py-4 flex items-start justify-between">
          <div className="min-w-0">
            <h3 className="text-sm font-medium text-ink-primary truncate">{title}</h3>
            {subtitle && <p className="text-xs text-ink-tertiary mt-0.5 truncate">{subtitle}</p>}
          </div>
          <button onClick={onClose} className="text-ink-tertiary hover:text-ink-primary shrink-0 ml-3">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}
