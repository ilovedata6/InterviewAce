"use client";

import { useState } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { AppNavbar } from "@/components/layout/app-navbar";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Toaster } from "@/components/ui/sonner";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // TODO: Replace with real user from auth context (Phase F4)
  const user = { full_name: "Demo User", email: "demo@interviewace.app" };
  const isAdmin = false;

  const handleLogout = () => {
    // TODO: Implement logout via auth store (Phase F4)
    console.log("logout");
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <div className="hidden lg:block">
        <AppSidebar isAdmin={isAdmin} />
      </div>

      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="w-64 p-0">
          <AppSidebar isAdmin={isAdmin} />
        </SheetContent>
      </Sheet>

      {/* Main area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <AppNavbar
          user={user}
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
          onLogout={handleLogout}
        />
        <main className="flex-1 overflow-y-auto bg-zinc-50 p-4 lg:p-6 dark:bg-zinc-900">
          {children}
        </main>
      </div>

      <Toaster richColors position="top-right" />
    </div>
  );
}
