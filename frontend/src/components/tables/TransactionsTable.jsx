import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Search, ArrowUpDown, ChevronLeft, ChevronRight, AlertCircle, Copy, Check } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import Badge from "@/components/ui/Badge";
import Input from "@/components/ui/Input";
import Skeleton from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";
import { cn } from "@/utils/cn";

const PAGE_SIZE = 8;

function CopyId({ id }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(String(id));
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* clipboard unavailable */
    }
  };
  return (
    <button
      onClick={copy}
      title="Copy ID"
      className="rounded-md p-1 text-slate-400 transition hover:bg-primary-50 hover:text-primary-600"
    >
      {copied ? <Check className="h-3.5 w-3.5 text-primary-600" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  );
}

export default function TransactionsTable({ rows = [], loading, error }) {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState({ key: "probability", dir: "desc" });
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    let data = rows.filter((r) =>
      [r.TransactionID, r.risk, r.label]
        .filter((v) => v != null)
        .some((v) => String(v).toLowerCase().includes(q))
    );
    data = [...data].sort((a, b) => {
      const av = a[sort.key], bv = b[sort.key];
      const cmp = typeof av === "number" ? av - bv : String(av).localeCompare(String(bv));
      return sort.dir === "asc" ? cmp : -cmp;
    });
    return data;
  }, [rows, query, sort]);

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const view = filtered.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  const toggleSort = (key) =>
    setSort((s) => ({ key, dir: s.key === key && s.dir === "desc" ? "asc" : "desc" }));

  const columns = [
    { key: "TransactionID", label: "Transaction ID" },
    { key: "probability", label: "Risk Score" },
    { key: "risk", label: "Risk Level" },
    { key: "label", label: "Prediction" },
  ];

  return (
    <GlassCard>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="font-semibold text-slate-900">Scored Transactions</h3>
        <div className="w-full max-w-xs">
          <Input
            icon={Search}
            placeholder="Search by ID, risk, prediction…"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(0);
            }}
          />
        </div>
      </div>

      {error ? (
        <EmptyState
          icon={AlertCircle}
          title="Couldn't load transactions"
          hint={`${error.message}. Make sure the API is running and you've scored a batch.`}
        />
      ) : !loading && rows.length === 0 ? (
        <EmptyState
          title="No transactions yet"
          hint="Upload a CSV in the Action Center to score transactions — results appear here."
        />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
                  {columns.map((c) => (
                    <th key={c.key} className="px-3 py-2 font-medium">
                      <button
                        onClick={() => toggleSort(c.key)}
                        className="inline-flex items-center gap-1 hover:text-slate-600"
                      >
                        {c.label}
                        <ArrowUpDown className="h-3 w-3 opacity-50" />
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: 6 }).map((_, i) => (
                      <tr key={i} className="border-b border-slate-100">
                        {columns.map((c) => (
                          <td key={c.key} className="px-3 py-3">
                            <Skeleton className="h-4 w-20" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : view.map((r, i) => (
                      <motion.tr
                        key={r.TransactionID}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.02 }}
                        className="border-b border-slate-100 hover:bg-slate-50"
                      >
                        <td className="px-3 py-3">
                          <span className="inline-flex items-center gap-1.5">
                            <span className="font-mono text-slate-600">#{r.TransactionID}</span>
                            <CopyId id={r.TransactionID} />
                          </span>
                        </td>
                        <td className="px-3 py-3 font-semibold text-slate-900">
                          {(r.probability * 100).toFixed(1)}
                        </td>
                        <td className="px-3 py-3">
                          <Badge tone={r.risk}>{r.risk}</Badge>
                        </td>
                        <td className="px-3 py-3">
                          <Badge tone={r.label}>{r.label}</Badge>
                        </td>
                      </motion.tr>
                    ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
            <span>{filtered.length} result{filtered.length !== 1 ? "s" : ""}</span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-lg border border-slate-200 p-1.5 hover:bg-slate-50 disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-slate-500">{page + 1} / {pages}</span>
              <button
                disabled={page >= pages - 1}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-lg border border-slate-200 p-1.5 hover:bg-slate-50 disabled:opacity-40"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </GlassCard>
  );
}
