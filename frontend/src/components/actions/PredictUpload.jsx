import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  X,
  Loader2,
  AlertCircle,
  Activity,
} from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import { API_BASE_URL } from "@/services/apiClient";
import { cn } from "@/utils/cn";

export default function PredictUpload() {
  const inputRef = useRef(null);
  const logContainerRef = useRef(null);
  const [file, setFile] = useState(null);
  const [drag, setDrag] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | processing | done | error
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const [logs, setLogs] = useState([]);
  const [driftRunning, setDriftRunning] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  // Auto-scroll the live log to the newest entry as transactions stream in.
  useEffect(() => {
    const el = logContainerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [logs, driftRunning]);

  const reset = () => {
    setStatus("idle");
    setProgress({ done: 0, total: 0 });
    setLogs([]);
    setDriftRunning(false);
    setMessage(null);
    setError(null);
  };

  const onFile = (f) => {
    if (f && f.name.endsWith(".csv")) {
      setFile(f);
      reset();
    }
  };

  const analyze = async () => {
    if (!file) return;
    reset();
    setStatus("processing");

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        body: form,
      });
      if (!res.ok || !res.body) throw new Error(`Server responded ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // Read the NDJSON stream line-by-line as transactions complete.
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();
        for (const line of lines) {
          if (!line.trim()) continue;
          let ev;
          try {
            ev = JSON.parse(line);
          } catch {
            continue;
          }
          if (ev.type === "start") {
            setProgress({ done: 0, total: ev.total });
          } else if (ev.type === "progress" || ev.type === "error") {
            setProgress({ done: ev.index, total: ev.total });
            setLogs((p) => [...p, ev]);
          } else if (ev.type === "drift") {
            setDriftRunning(ev.status === "start");
            setLogs((p) => [...p, ev]);
          } else if (ev.type === "done") {
            setMessage(ev.message);
            setStatus("done");
          }
        }
      }
      setDriftRunning(false);
      setStatus((s) => (s === "processing" ? "done" : s));
    } catch (e) {
      setError(e.message);
      setDriftRunning(false);
      setStatus("error");
    }
  };

  const pct = progress.total
    ? Math.round((progress.done / progress.total) * 100)
    : 0;
  const busy = status === "processing";

  return (
    <GlassCard>
      <div className="mb-4 flex items-center gap-2">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary-50 text-primary-600">
          <UploadCloud className="h-5 w-5" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900">Predict from CSV</h3>
          <p className="text-xs text-slate-500">
            Upload a transactions file to run the fraud pipeline
          </p>
        </div>
        <span className="ml-auto rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[10px] text-slate-500">
          POST /predict
        </span>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          onFile(e.dataTransfer.files?.[0]);
        }}
        onClick={() => !busy && inputRef.current?.click()}
        className={cn(
          "flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition",
          busy
            ? "cursor-not-allowed border-slate-200 bg-slate-50"
            : "cursor-pointer",
          drag
            ? "border-primary-500 bg-primary-50"
            : !busy && "border-slate-300 bg-slate-50 hover:border-primary-300"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          hidden
          onChange={(e) => onFile(e.target.files?.[0])}
        />
        <motion.div
          animate={drag ? { y: -6 } : { y: 0 }}
          className="grid h-14 w-14 place-items-center rounded-xl bg-primary-100 text-primary-600"
        >
          <UploadCloud className="h-6 w-6" />
        </motion.div>
        <p className="mt-3 text-sm font-medium text-slate-700">
          Drag &amp; drop your CSV here
        </p>
        <p className="text-xs text-slate-400">or click to browse</p>
      </div>

      <AnimatePresence>
        {file && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 overflow-hidden"
          >
            <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3">
              <FileSpreadsheet className="h-8 w-8 text-primary-600" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-800">
                  {file.name}
                </p>
                <p className="text-xs text-slate-400">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
              {status === "done" ? (
                <CheckCircle2 className="h-5 w-5 text-primary-600" />
              ) : (
                !busy && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                      reset();
                    }}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Live progress + per-transaction log */}
      {(busy || logs.length > 0) && (
        <div className="mt-4">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-slate-600">
              {busy ? "Processing transactions…" : "Finished"}
            </span>
            <span className="font-medium text-slate-700">
              {progress.done}/{progress.total}
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <motion.div
              className="h-full rounded-full bg-primary-600"
              animate={{ width: `${pct}%` }}
            />
          </div>

          {/* Drift-analysis indicator */}
          <AnimatePresence>
            {driftRunning && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="mt-3 flex items-center gap-2 rounded-xl border border-primary-200 bg-primary-50 px-3 py-2 text-sm font-medium text-primary-700"
              >
                <Loader2 className="h-4 w-4 animate-spin" />
                Drift limit reached — drift analysis running…
              </motion.div>
            )}
          </AnimatePresence>

          <div
            ref={logContainerRef}
            className="mt-3 max-h-52 space-y-1 overflow-auto rounded-xl border border-slate-200 bg-slate-50 p-2 scroll-smooth"
          >
            {logs.map((l, i) => {
              if (l.type === "drift") {
                return (
                  <div
                    key={i}
                    className="flex items-center gap-2 rounded-lg px-2 py-1 text-sm font-medium text-primary-700"
                  >
                    {l.status === "start" ? (
                      <Activity className="h-3.5 w-3.5" />
                    ) : (
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    )}
                    <span>{l.message}</span>
                  </div>
                );
              }
              if (l.type === "error") {
                return (
                  <div key={i} className="rounded-lg px-2 py-1 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600">
                        <span className="font-mono text-slate-400">#{l.index}</span>{" "}
                        {l.transaction_id != null
                          ? `Transaction ${l.transaction_id}`
                          : "row"}
                      </span>
                      <span className="flex items-center gap-1 text-xs font-medium text-rose-500">
                        <AlertCircle className="h-3.5 w-3.5" /> failed
                      </span>
                    </div>
                    {l.message && (
                      <p
                        className="mt-0.5 truncate text-xs text-slate-400"
                        title={l.message}
                      >
                        {l.message}
                      </p>
                    )}
                  </div>
                );
              }
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between rounded-lg px-2 py-1 text-sm"
                >
                  <span className="text-slate-600">
                    <span className="font-mono text-slate-400">#{l.index}</span>{" "}
                    {l.transaction_id != null
                      ? `Transaction ${l.transaction_id}`
                      : "row"}
                  </span>
                  <span className="flex items-center gap-2">
                    {l.probability != null && (
                      <span className="text-xs text-slate-500">
                        {(l.probability * 100).toFixed(1)}
                      </span>
                    )}
                    {l.label && <Badge tone={l.label}>{l.label}</Badge>}
                  </span>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Completion banner */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 flex items-center gap-2 rounded-xl border border-primary-200 bg-primary-50 px-4 py-3 text-sm font-medium text-primary-700"
          >
            <CheckCircle2 className="h-5 w-5" />
            {message}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-4 flex items-center gap-3">
        <Button onClick={analyze} disabled={!file || busy}>
          {busy ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Analyzing…
            </>
          ) : (
            "Analyze Dataset"
          )}
        </Button>
        {error && <span className="text-sm text-slate-500">{error}</span>}
      </div>
    </GlassCard>
  );
}
