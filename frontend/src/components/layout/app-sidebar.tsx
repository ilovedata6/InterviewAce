"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  User,
  Shield,
  BarChart3,
  Sparkles,
} from "lucide-react";
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
    <aside className="flex h-full w-64 flex-col border-r border-zinc-200/70 bg-white dark:border-zinc-800/70 dark:bg-zinc-950">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-zinc-200/70 px-5 dark:border-zinc-800/70">
        <Link href={ROUTES.DASHBOARD} className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 shadow-sm">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Interview
            <span className="bg-gradient-to-r from-blue-600 via-violet-600 to-blue-500 bg-clip-text text-transparent">
              Ace
            </span>
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-2 px-3 text-[11px] font-semibold tracking-widest text-zinc-400 uppercase dark:text-zinc-500">
          Menu
        </p>
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-gradient-to-r from-blue-50 to-blue-50/50 text-blue-700 shadow-sm dark:from-blue-950/60 dark:to-blue-950/30 dark:text-blue-300"
                  : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-900/50 dark:hover:text-zinc-50",
              )}
            >
              <item.icon
                className={cn("h-[18px] w-[18px]", isActive && "text-blue-600 dark:text-blue-400")}
              />
              {item.title}
            </Link>
          );
        })}

        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="my-4 px-3">
              <div className="h-px bg-zinc-200/80 dark:bg-zinc-800/80" />
            </div>
            <p className="mb-2 px-3 text-[11px] font-semibold tracking-widest text-zinc-400 uppercase dark:text-zinc-500">
              Admin
            </p>
            {adminItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-gradient-to-r from-blue-50 to-blue-50/50 text-blue-700 shadow-sm dark:from-blue-950/60 dark:to-blue-950/30 dark:text-blue-300"
                      : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-900/50 dark:hover:text-zinc-50",
                  )}
                >
                  <item.icon
                    className={cn(
                      "h-[18px] w-[18px]",
                      isActive && "text-blue-600 dark:text-blue-400",
                    )}
                  />
                  {item.title}
                </Link>
              );
            })}
          </>
        )}
      </nav>

      {/* Bottom brand */}
      <div className="border-t border-zinc-200/70 px-5 py-4 dark:border-zinc-800/70">
        <p className="text-[11px] text-zinc-400 dark:text-zinc-500">
          &copy; {new Date().getFullYear()} InterviewAce
        </p>
      </div>
    </aside>
  );
}
