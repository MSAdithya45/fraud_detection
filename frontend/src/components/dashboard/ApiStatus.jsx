import { Server } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import { useApiHealth } from "@/hooks/useFraudData";
import { API_BASE_URL } from "@/services/apiClient";
import { cn } from "@/utils/cn";

export default function ApiStatus() {
  const { data, isLoading, isError } = useApiHealth();
  const online = !!data?.online && !isError;

  const state = isLoading
    ? { label: "Checking…", dot: "bg-slate-300", text: "text-slate-500" }
    : online
    ? { label: "Operational", dot: "bg-primary-600", text: "text-primary-700" }
    : { label: "Unreachable", dot: "bg-slate-400", text: "text-slate-500" };

  return (
    <GlassCard>
      <div className="mb-4 flex items-center gap-2">
        <Server className="h-5 w-5 text-primary-600" />
        <h3 className="font-semibold text-slate-900">API Status</h3>
      </div>

      <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-3 py-3">
        <div>
          <p className="text-sm font-medium text-slate-700">FastAPI Backend</p>
          <p className="truncate text-xs text-slate-400">{API_BASE_URL}</p>
        </div>
        <span className={cn("flex items-center gap-2 text-sm font-medium", state.text)}>
          <span className="relative flex h-2.5 w-2.5">
            {online && (
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary-400 opacity-60" />
            )}
            <span className={cn("relative inline-flex h-2.5 w-2.5 rounded-full", state.dot)} />
          </span>
          {state.label}
        </span>
      </div>

      {online && data?.latency != null && (
        <p className="mt-3 text-xs text-slate-400">
          Response time: <span className="font-medium text-slate-600">{data.latency} ms</span>
        </p>
      )}
    </GlassCard>
  );
}
