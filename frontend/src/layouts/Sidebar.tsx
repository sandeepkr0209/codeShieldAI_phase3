import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  ScanLine,
  ShieldAlert,
  Radar,
  FileText,
  BookOpen,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { cn } from "../lib/utils";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/scans", label: "Scans", icon: ScanLine },
  { to: "/findings", label: "Findings", icon: ShieldAlert },
  { to: "/attack-surface", label: "Attack Surface", icon: Radar },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/knowledge-base", label: "Knowledge", icon: BookOpen },
];

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 h-screen sticky top-0 border-r border-border bg-surface flex flex-col">
      <div className="h-14 flex items-center gap-2 px-4 border-b border-border">
        <div className="h-6 w-6 rounded bg-primary/15 flex items-center justify-center">
          <ShieldCheck className="h-3.5 w-3.5 text-primary" />
        </div>
        <span className="text-[13px] font-semibold text-ink-primary tracking-tight">CodeShieldAI</span>
      </div>

      <nav className="flex-1 px-2.5 py-3 space-y-0.5">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => cn("nav-item", isActive ? "nav-item-active" : "nav-item-inactive")}
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="px-2.5 py-3 border-t border-border">
        <NavLink
          to="/settings"
          className={({ isActive }) => cn("nav-item", isActive ? "nav-item-active" : "nav-item-inactive")}
        >
          <Settings className="h-4 w-4 shrink-0" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
