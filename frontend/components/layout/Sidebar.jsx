"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";
import { useAuthStore } from "@/stores/authStore";
import { LayoutDashboard, FolderKanban, Grid3x3, FlaskConical, LogOut, Menu, X, ChevronLeft, ChevronRight } from "lucide-react";
import Button from "@/components/ui/Button";
import { useState } from "react";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Workspaces",
    href: "/dashboard/workspaces",
    icon: FolderKanban,
  },
  {
    title: "Grids",
    href: "/dashboard/grids",
    icon: Grid3x3,
  },
  {
    title: "Scenarios",
    href: "/dashboard/scenarios",
    icon: FlaskConical,
  },
];

export function Sidebar({ isCollapsed = false, onToggleCollapse }) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    window.location.href = "/auth/login";
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-gradient-to-b from-card to-card/95 backdrop-blur-sm">
      {/* Logo Section */}
      <div className="p-6 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 min-w-0 flex-1">
            <div className="relative flex-shrink-0">
              <div className="absolute inset-0 bg-gradient-to-br from-primary to-primary/80 rounded-xl blur-sm opacity-75"></div>
              <div className="relative rounded-xl bg-gradient-to-br from-primary to-primary/90 p-3 shadow-lg">
                <Grid3x3 className="h-7 w-7 text-primary-foreground" />
              </div>
            </div>
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <h2 className="font-bold text-xl leading-tight text-foreground">SmartGrid</h2>
                <p className="text-xs text-muted-foreground/80 font-medium">Management System</p>
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="flex-shrink-0 hover:bg-primary/10 hover:text-primary transition-colors duration-200"
              onClick={onToggleCollapse}
            >
              {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setIsMobileOpen(false)}
              className={cn(
                "group flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-300 ease-out relative overflow-hidden",
                isCollapsed ? "justify-center px-2" : "",
                isActive
                  ? "bg-gradient-to-r from-primary/10 to-primary/5 text-primary shadow-sm border-l-4 border-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-primary/5 hover:shadow-md hover:scale-[1.02]"
              )}
            >
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-50"></div>
              )}
              <div className={cn(
                "relative z-10 p-1 rounded-lg transition-colors duration-200",
                isActive ? "bg-primary/20" : "group-hover:bg-primary/10"
              )}>
                <Icon className="h-5 w-5" />
              </div>
              {!isCollapsed && <span className="font-semibold text-sm relative z-10">{item.title}</span>}
              {isActive && !isCollapsed && (
                <div className="absolute right-2 top-1/2 -translate-y-1/2 w-2 h-2 bg-primary rounded-full animate-pulse"></div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Profile & Logout */}
      <div className="p-4 border-t border-border/50">
        <div className={cn(
          "bg-gradient-to-r from-muted/50 to-muted/30 rounded-xl p-4 mb-4 shadow-inner",
          isCollapsed ? "p-2" : ""
        )}>
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/30 to-primary/10 rounded-full blur-sm"></div>
              <div className="relative h-12 w-12 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center border-2 border-primary/20">
                <span className="text-primary font-bold text-lg">{user?.email?.[0]?.toUpperCase() || "U"}</span>
              </div>
            </div>
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm text-foreground truncate">{user?.name || user?.email || "User"}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
            )}
          </div>
        </div>
        {!isCollapsed && (
          <Button
            onClick={handleLogout}
            variant="outline"
            className="w-full bg-transparent border-border/50 hover:bg-destructive/10 hover:border-destructive/30 hover:text-destructive transition-all duration-200 shadow-sm"
            size="sm"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-6 left-6 z-50">
        <Button
          variant="outline"
          size="icon"
          className="bg-card/90 backdrop-blur-md border-border/50 shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 hover:bg-primary/5"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
        >
          <div className="relative">
            {isMobileOpen ? (
              <X className="h-5 w-5 transition-transform duration-200 rotate-0 hover:rotate-90" />
            ) : (
              <Menu className="h-5 w-5 transition-transform duration-200" />
            )}
          </div>
        </Button>
      </div>

      {/* Mobile sidebar overlay */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-background/60 backdrop-blur-sm z-40 transition-opacity duration-300"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={cn(
          "lg:hidden fixed top-0 left-0 h-full w-80 bg-card/95 backdrop-blur-xl border-r border-border/50 z-40 flex flex-col shadow-2xl transition-transform duration-300 ease-out",
          isMobileOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside
        className={cn(
          "hidden lg:flex fixed top-0 left-0 h-full bg-card/95 backdrop-blur-xl border-r border-border/50 z-30 flex flex-col shadow-xl transition-all duration-300 ease-out",
          isCollapsed ? "w-28" : "w-80"
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
