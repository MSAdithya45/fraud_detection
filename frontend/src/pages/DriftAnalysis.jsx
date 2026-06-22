import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Download, Database, FileDown, AlertCircle } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import EmptyState from "@/components/ui/EmptyState";
import Skeleton from "@/components/ui/Skeleton";
import { fraudApi } from "@/services/fraudApi";
import { API_BASE_URL } from "@/services/apiClient";
import { cn } from "@/utils/cn";

const TABS = [
  { key: "low", label: "Low Drift" },
  { key: "medium", label: "Medium Drift" },
  { key: "high", label: "High Drift" },
];

const COLUMNS = [
  { key: "iso_drift_score", label: "ISO" },
  { key: "ae_drift_score", label: "AE" },
  { key: "rules_drift_score", label: "Rules" },
  { key: "feature_drift_score", label: "Feature" },
  { key: "final_drift_score", label: "Final" },
];

const fmtScore = (n) => (n == null ? "—" : Number(n).toFixed(4));
const fmtDate = (s) => {
  if (!s) return "—";
  const d = new Date(s.replace(" ", "T"));
  return isNaN(d) ? String(s).slice(0, 19) : d.toLocaleString();
};

// Styled <a> so the browser handles the download via Content-Disposition.
function DownloadLink({ href, children, variant = "primary", className }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg px-4 h-11 text-sm font-medium transition-colors";
  const styles =
    variant === "primary"
      ? "bg-primary-600 text-white hover:bg-primary-700"
      : "border border-slate-300 bg-yellow-100 text-orange-700 hover:bg-orange-200 hover:border-orange-300";
  return (
    <a href={href} className={cn(base, styles, className)}>
      {children}
    </a>
  );
}

export default function DriftAnalysis() {
  const [tab, setTab] = useState("low");

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["drift", tab],
    queryFn: () => fraudApi.getDrift(tab),
    retry: false,
  });

  const rows = Array.isArray(data) ? data : [];

  return (
    <div className="space-y-5">
      {/* ---- History exports ---- */}
      <GlassCard className="flex flex-wrap items-center gap-3">
        <div className="mr-auto flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-primary-50 text-primary-600">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">History Exports</h3>
            <p className="text-xs text-slate-500">
              Download the complete raw or preprocessed transaction history
            </p>
          </div>
        </div>
        <DownloadLink href={`${API_BASE_URL}/history/raw`} variant="outline">
          <Download className="h-4 w-4" /> Download full raw data
        </DownloadLink>
        <DownloadLink href={`${API_BASE_URL}/history/processed`}>
          <Download className="h-4 w-4" /> Download full preprocessed data
        </DownloadLink>
      </GlassCard>

      {/* ---- Drift records ---- */}
      <GlassCard>
        <div className="mb-4 flex flex-wrap items-center gap-2">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
                tab === t.key
                  ? "bg-primary-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>

        {isError ? (
          <EmptyState
            icon={AlertCircle}
            title="Couldn't load drift records"
            hint={error?.message}
          />
        ) : !isLoading && rows.length === 0 ? (
          <EmptyState
            title="No drift records yet"
            hint="A drift row is created each time a chunk crosses the threshold."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
                  {COLUMNS.map((c) => (
                    <th key={c.key} className="px-3 py-2 font-medium">
                      {c.label} Drift
                    </th>
                  ))}
                  <th className="px-3 py-2 font-medium">Analysed At</th>
                  <th className="px-3 py-2 text-right font-medium">Dataset</th>
                </tr>
              </thead>
              <tbody>
                {isLoading
                  ? Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i} className="border-b border-slate-100">
                        {Array.from({ length: 7 }).map((__, j) => (
                          <td key={j} className="px-3 py-3">
                            <Skeleton className="h-4 w-16" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : rows.map((r, i) => (
                      <motion.tr
                        key={r.id ?? i}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.02 }}
                        className="border-b border-slate-100 hover:bg-slate-50"
                      >
                        {COLUMNS.map((c) => (
                          <td
                            key={c.key}
                            className={cn(
                              "px-3 py-3",
                              c.key === "final_drift_score"
                                ? "font-semibold text-slate-900"
                                : "text-slate-600"
                            )}
                          >
                            {fmtScore(r[c.key])}
                          </td>
                        ))}
                        <td className="px-3 py-3 text-slate-500">
                          {fmtDate(r.created_at)}
                        </td>
                        <td className="px-3 py-3 text-right">
                          <a
                            href={`${API_BASE_URL}/drift/${tab}/${r.id}/download`}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 transition hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700"
                          >
                            <FileDown className="h-3.5 w-3.5" /> Download
                          </a>
                        </td>
                      </motion.tr>
                    ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
