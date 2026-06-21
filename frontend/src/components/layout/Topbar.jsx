import { useLocation } from "react-router-dom";
import { Menu, Search, ChevronRight } from "lucide-react";
import { pageMeta } from "./navConfig";

export default function Topbar({ onMenu }) {
  const { pathname } = useLocation();
  const meta = pageMeta[pathname] || { title: "FraudLens", crumb: "Home" };

  return (
    <header className="sticky top-0 z-30 px-3 pt-3">
      <div className="card flex items-center gap-3 px-4 py-3">
        <button onClick={onMenu} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden">
          <Menu className="h-5 w-5" />
        </button>

        <div className="min-w-0">
          <h1 className="truncate text-lg font-bold tracking-tight text-slate-900">{meta.title}</h1>
          <div className="flex items-center gap-1 text-[11px] text-slate-400">
            <span>FraudLens</span>
            <ChevronRight className="h-3 w-3" />
            <span className="text-slate-500">{meta.crumb}</span>
          </div>
        </div>

        <div className="relative mx-auto hidden w-full max-w-md md:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            placeholder="Search transactions, IDs…"
            className="h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 outline-none focus:border-primary-500 focus:bg-white focus:ring-2 focus:ring-primary-500/20"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-full bg-primary-100 text-sm font-semibold text-primary-700">
            BA
          </div>
        </div>
      </div>
    </header>
  );
}
