import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Search } from "lucide-react";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import EmptyState from "@/components/ui/EmptyState";
import { fraudApi } from "@/services/fraudApi";

function DivergingBars({ features }) {
  const top = useMemo(() => {
    const list = [...features]
      .map((f) => ({
        feature: f.feature,
        impact: Number(f.impact ?? 0),
        abs: Math.abs(Number(f.absolute_impact ?? f.impact ?? 0)),
      }))
      .sort((a, b) => b.abs - a.abs)
      .slice(0, 12);
    const maxAbs = Math.max(...list.map((f) => f.abs), 1e-9);
    return list.map((f) => ({ ...f, width: (f.abs / maxAbs) * 50 }));
  }, [features]);

  return (
    <div>
      <div className="mb-3 flex items-center justify-center gap-5 text-[11px] text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm bg-primary-300" /> Pushes toward Legit
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm bg-primary-600" /> Pushes toward Fraud
        </span>
      </div>
      <div className="space-y-2">
        {top.map((f, i) => (
          <motion.div
            key={f.feature}
            initial={{ opacity: 0, x: 6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.03 }}
            className="grid grid-cols-[100px_1fr_60px] items-center gap-2"
          >
            <span title={f.feature} className="truncate text-right text-xs font-medium text-slate-600">
              {f.feature}
            </span>
            <div className="relative h-5 rounded bg-slate-100">
              <div className="absolute left-1/2 top-0 h-full w-px bg-slate-300" />
              {f.impact >= 0 ? (
                <div
                  className="absolute left-1/2 top-0 h-full rounded-r bg-primary-600"
                  style={{ width: `${f.width}%` }}
                />
              ) : (
                <div
                  className="absolute right-1/2 top-0 h-full rounded-l bg-primary-300"
                  style={{ width: `${f.width}%` }}
                />
              )}
            </div>
            <span className="text-right font-mono text-[11px] text-slate-500">
              {f.impact.toFixed(3)}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default function ShapByIdCard() {
  const [id, setId] = useState("");
  const [state, setState] = useState({ loading: false, data: null, error: null });

  const run = async () => {
    if (!id) return;
    setState({ loading: true, data: null, error: null });
    try {
      const data = await fraudApi.getTransactionShap(id);
      const features = Array.isArray(data?.shap) ? data.shap : [];
      if (data?.error || !features.length) {
        setState({ loading: false, data: null, error: data?.error || "No SHAP explanation found" });
      } else {
        setState({ loading: false, data: features, error: null });
      }
    } catch (e) {
      setState({ loading: false, data: null, error: e.message });
    }
  };

  return (
    <div>
      <div className="flex gap-2">
        <Input
          icon={Search}
          placeholder="Enter Transaction ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <Button onClick={run} disabled={!id || state.loading} className="shrink-0">
          {state.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Explain"}
        </Button>
      </div>

      <AnimatePresence mode="wait">
        {state.data ? (
          <motion.div
            key="bars"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-5"
          >
            <DivergingBars features={state.data} />
          </motion.div>
        ) : state.error ? (
          <EmptyState title="No explanation" hint={state.error} />
        ) : (
          <p className="mt-6 text-center text-sm text-slate-400">
            Enter a transaction ID to view its feature-level fraud drivers.
          </p>
        )}
      </AnimatePresence>
    </div>
  );
}
