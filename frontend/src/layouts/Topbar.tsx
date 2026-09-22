import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Bell, User as UserIcon, LogOut, Settings as SettingsIcon, ChevronDown } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { Breadcrumb } from "../components/Breadcrumb";
import { CommandSearch } from "../components/CommandSearch";

export function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  const initials = user?.name
    ? user.name.trim().split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase()).join("")
    : "?";

  return (
    <header className="h-14 sticky top-0 z-10 border-b border-border bg-background/90 backdrop-blur flex items-center justify-between px-5 gap-4">
      <Breadcrumb />

      <div className="flex items-center gap-3 shrink-0">
        <CommandSearch />

        <button className="relative h-8 w-8 rounded-md border border-border flex items-center justify-center text-ink-tertiary hover:text-ink-primary hover:bg-surface-alt transition-colors">
          <Bell className="h-3.5 w-3.5" />
        </button>

        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="flex items-center gap-2 h-8 pl-1 pr-2 rounded-md border border-border hover:bg-surface-alt transition-colors"
          >
            {user?.profile_image ? (
              <img src={user.profile_image} alt="" className="h-6 w-6 rounded object-cover" />
            ) : (
              <div className="h-6 w-6 rounded bg-primary/15 flex items-center justify-center text-primary text-[10px] font-medium">
                {initials}
              </div>
            )}
            <span className="text-sm text-ink-secondary hidden sm:inline max-w-[100px] truncate">
              {user?.name ?? "Account"}
            </span>
            <ChevronDown className="h-3 w-3 text-ink-tertiary" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 mt-2 w-56 card-raised p-1.5 shadow-popover z-20">
              <div className="px-3 py-2 border-b border-border mb-1">
                <p className="text-sm text-ink-primary truncate">{user?.name}</p>
                <p className="text-xs text-ink-tertiary truncate">{user?.email}</p>
              </div>
              <button
                onClick={() => { setMenuOpen(false); navigate("/settings"); }}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm text-ink-secondary hover:bg-surface-alt transition-colors text-left"
              >
                <UserIcon className="h-3.5 w-3.5" />
                Profile
              </button>
              <button
                onClick={() => { setMenuOpen(false); navigate("/settings"); }}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm text-ink-secondary hover:bg-surface-alt transition-colors text-left"
              >
                <SettingsIcon className="h-3.5 w-3.5" />
                Settings
              </button>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm text-critical hover:bg-critical/10 transition-colors text-left"
              >
                <LogOut className="h-3.5 w-3.5" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
