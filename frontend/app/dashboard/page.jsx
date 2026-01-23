"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../../stores/authStore";
import { Sidebar } from "../../components/layout/Sidebar";
import { DashboardHeader } from "../../components/layout/DashboardHeader";
import { toast } from "sonner";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout, checkAuth } = useAuthStore();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      checkAuth().catch(() => {
        // If checkAuth fails, stay on page but don't redirect
      });
    }
  }, [isAuthenticated, checkAuth]);

  useEffect(() => {
    if (isAuthenticated && user && !user.email_verified) {
      router.push("/verify-email-pending");
    }
  }, [isAuthenticated, user, router]);

  const handleLogout = async () => {
    await logout();
    toast.success("Logged out successfully.");
    router.push("/");
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar isCollapsed={isSidebarCollapsed} onToggleCollapse={toggleSidebar} />
      <div className="flex-1 flex flex-col">
        <DashboardHeader onToggleSidebar={toggleSidebar} isSidebarCollapsed={isSidebarCollapsed} />
        <main className={`flex-1 p-8 transition-all duration-300 ${isSidebarCollapsed ? 'lg:ml-28' : 'lg:ml-80'}`}>
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-6">
              Welcome to SmartGrid Management System
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {/* Mock Cards */}
              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-card-foreground mb-2">
                  Grid Status
                </h3>
                <p className="text-muted-foreground">
                  All systems operational. 99.9% uptime.
                </p>
              </div>

              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-card-foreground mb-2">
                  Energy Consumption
                </h3>
                <p className="text-muted-foreground">
                  Current load: 2.4 MW
                </p>
              </div>

              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-card-foreground mb-2">
                  Alerts
                </h3>
                <p className="text-muted-foreground">
                  No active alerts.
                </p>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-card-foreground mb-4">
                Recent Activity
              </h2>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <p className="text-sm text-muted-foreground">
                    Grid optimization completed successfully
                  </p>
                  <span className="text-xs text-muted-foreground ml-auto">
                    2 hours ago
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <p className="text-sm text-muted-foreground">
                    Maintenance scheduled for Sector 7
                  </p>
                  <span className="text-xs text-muted-foreground ml-auto">
                    1 day ago
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <p className="text-sm text-muted-foreground">
                    Peak demand forecast updated
                  </p>
                  <span className="text-xs text-muted-foreground ml-auto">
                    3 days ago
                  </span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
