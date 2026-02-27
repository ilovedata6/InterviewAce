"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FileText, MessageSquare, User, Shield, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";

const navItems = [
  {
    title: "Dashboard",
    href: ROUTES.DASHBOARD,
    icon: LayoutDashboard,
  },
  {
    title: "Resumes",
    href: ROUTES.RESUMES,
    icon: FileText,
  },
  {
    title: "Interviews",
    href: ROUTES.INTERVIEWS,
    icon: MessageSquare,
  },
  {
    title: "Profile",
    href: ROUTES.PROFILE,
    icon: User,
  },
];

const adminItems = [
  {
    title: "Users",
    href: ROUTES.ADMIN_USERS,
    icon: Shield,
  },
  {
    title: "Statistics",
    href: ROUTES.ADMIN_STATS,
    icon: BarChart3,
  },
];

interface AppSidebarProps {
  isAdmin?: boolean;
}

export function AppSidebar({ isAdmin = false }: AppSidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col border-r bg-white dark:border-zinc-800 dark:bg-zinc-950">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6 dark:border-zinc-800">
        <Link href={ROUTES.DASHBOARD} className="flex items-center gap-2">
          <span className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Interview<span className="text-blue-600">Ace</span>
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-2 px-3 text-xs font-semibold tracking-wider text-zinc-500 uppercase">
          Menu
        </p>
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-50",
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.title}
            </Link>
          );
        })}

        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="my-4">
              <div className="h-px bg-zinc-200 dark:bg-zinc-800" />
            </div>
            <p className="mb-2 px-3 text-xs font-semibold tracking-wider text-zinc-500 uppercase">
              Admin
            </p>
            {adminItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                      : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-50",
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.title}
                </Link>
              );
            })}
          </>
        )}
      </nav>
    </aside>
  );
}
