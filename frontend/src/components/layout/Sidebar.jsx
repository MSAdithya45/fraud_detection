import { NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, ChevronLeft, X } from "lucide-react";
import { navItems } from "./navConfig";
import { cn } from "@/utils/cn";

function NavList({ collapsed, onNavigate }) {
  return (
    <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-3 py-2">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary-50 text-primary-700"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
            )
          }
        >
          {({ isActive }) => (
            <>
              {isActive && (
                <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-primary-600" />
              )}
              <item.icon className="h-5 w-5 shrink-0" />
              <AnimatePresence initial={false}>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: "auto" }}
                    exit={{ opacity: 0, width: 0 }}
                    className="overflow-hidden whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

function Brand({ collapsed }) {
  return (
    <div className="flex items-center gap-3 border-b border-slate-100 px-5 py-5">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary-600">
        <ShieldCheck className="h-5 w-5 text-white" />
      </div>
      {!collapsed && (
        <div className="leading-tight">
          <p className="text-base font-bold tracking-tight text-slate-900">FraudLens</p>
          <p className="text-[11px] text-slate-400">Fraud Detection</p>
        </div>
      )}
    </div>
  );
}

function ProfileCard({ collapsed }) {
  return (
    <div className="border-t border-slate-100 p-3">
      <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-2.5">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary-100 text-sm font-semibold text-primary-700">
          BA
        </div>
        {!collapsed && (
          <div className="min-w-0 leading-tight">
            <p className="truncate text-sm font-semibold text-slate-800">Bank Employee</p>
            <p className="truncate text-xs text-slate-400">Risk Analyst</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Sidebar({ collapsed, setCollapsed, mobileOpen, setMobileOpen }) {
  return (
    <>
      <motion.aside
        animate={{ width: collapsed ? 84 : 264 }}
        transition={{ type: "spring", stiffness: 260, damping: 30 }}
        className="sticky top-0 hidden h-screen shrink-0 p-3 lg:block"
      >
        <div className="card relative flex h-full flex-col">
          <Brand collapsed={collapsed} />
          <NavList collapsed={collapsed} />
          <ProfileCard collapsed={collapsed} />
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="absolute -right-3 top-20 grid h-6 w-6 place-items-center rounded-full border border-slate-200 bg-white text-slate-500 shadow-sm hover:text-primary-600"
          >
            <ChevronLeft className={cn("h-4 w-4 transition-transform", collapsed && "rotate-180")} />
          </button>
        </div>
      </motion.aside>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              className="fixed inset-0 z-40 bg-slate-900/30 lg:hidden"
            />
            <motion.aside
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: "spring", stiffness: 300, damping: 32 }}
              className="fixed inset-y-0 left-0 z-50 w-72 p-3 lg:hidden"
            >
              <div className="card flex h-full flex-col">
                <div className="flex items-center justify-between pr-3">
                  <Brand collapsed={false} />
                  <button
                    onClick={() => setMobileOpen(false)}
                    className="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <NavList collapsed={false} onNavigate={() => setMobileOpen(false)} />
                <ProfileCard collapsed={false} />
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
