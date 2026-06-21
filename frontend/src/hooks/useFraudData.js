import { useMemo } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fraudApi } from "@/services/fraudApi";
import { API_BASE_URL } from "@/services/apiClient";
import { riskFromProbability } from "@/utils/format";

const normalizeTxn = (t) => {
  const probability = Number(t.probability ?? 0);
  return {
    ...t,
    probability,
    label: t.label || (t.prediction === 1 ? "FRAUD" : "LEGIT"),
    risk: riskFromProbability(probability),
  };
};

/** Real transactions from the backend. No mock fallback. */
export function useTransactions() {
  return useQuery({
    queryKey: ["transactions"],
    queryFn: async () => {
      const data = await fraudApi.getTransactions();
      return Array.isArray(data) ? data.map(normalizeTxn) : [];
    },
    staleTime: 20000,
  });
}

/** KPIs + risk buckets derived entirely from real transaction rows. */
export function useDashboardStats() {
  const query = useTransactions();
  const rows = query.data || [];

  const stats = useMemo(() => {
    const total = rows.length;
    const fraud = rows.filter((r) => r.label === "FRAUD").length;
    const high = rows.filter((r) => r.risk === "High").length;
    const medium = rows.filter((r) => r.risk === "Medium").length;
    const low = total - high - medium;
    const avgScore =
      total > 0
        ? (rows.reduce((s, r) => s + r.probability, 0) / total) * 100
        : 0;

    return {
      total,
      fraud,
      fraudRate: total > 0 ? (fraud / total) * 100 : 0,
      avgScore,
      high,
      distribution: [
        { name: "Low", value: low },
        { name: "Medium", value: medium },
        { name: "High", value: high },
      ],
    };
  }, [rows]);

  return { ...query, rows, stats };
}

/** Global SHAP feature importance, aggregated from real /shap rows. */
export function useShapImportance(limit = 10) {
  return useQuery({
    queryKey: ["shap-importance"],
    queryFn: async () => {
      const rows = await fraudApi.getAllShap();
      if (!Array.isArray(rows) || !rows.length) return [];
      const acc = new Map();
      for (const r of rows) {
        const f = r.feature;
        const v = Math.abs(Number(r.absolute_impact ?? r.impact ?? 0));
        const cur = acc.get(f) || { sum: 0, n: 0 };
        cur.sum += v;
        cur.n += 1;
        acc.set(f, cur);
      }
      return [...acc.entries()]
        .map(([feature, { sum, n }]) => ({ feature, importance: sum / n }))
        .sort((a, b) => b.importance - a.importance)
        .slice(0, limit);
    },
    staleTime: 60000,
  });
}

/** Real reachability probe against the FastAPI server. */
export function useApiHealth() {
  return useQuery({
    queryKey: ["api-health"],
    queryFn: async () => {
      const started = performance.now();
      const res = await fetch(`${API_BASE_URL}/openapi.json`, {
        method: "GET",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return { online: true, latency: Math.round(performance.now() - started) };
    },
    refetchInterval: 15000,
    retry: false,
  });
}

export function useTransactionShap(id, enabled) {
  return useQuery({
    queryKey: ["shap", id],
    queryFn: () => fraudApi.getTransactionShap(id),
    enabled: !!id && enabled,
    retry: false,
  });
}

export function useLlmExplanation(id, enabled) {
  return useQuery({
    queryKey: ["llm", id],
    queryFn: () => fraudApi.getLlmExplanation(id),
    enabled: !!id && enabled,
    retry: false,
  });
}

export function usePredictCsv() {
  return useMutation({
    mutationFn: ({ file, onUploadProgress }) =>
      fraudApi.predictCsv(file, onUploadProgress),
  });
}
