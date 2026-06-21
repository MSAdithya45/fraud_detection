import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2 } from "lucide-react";
import ActionCard from "./ActionCard";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

/** Generic "enter an ID → fetch → show JSON result" action card. */
export default function FetchByIdCard({
  icon,
  title,
  description,
  endpoint,
  fetcher,
  buttonLabel = "Fetch",
  delay = 0,
}) {
  const [id, setId] = useState("");
  const [state, setState] = useState({ loading: false, data: null, error: null });

  const run = async () => {
    if (!id) return;
    setState({ loading: true, data: null, error: null });
    try {
      const data = await fetcher(id);
      setState({ loading: false, data, error: null });
    } catch (e) {
      setState({ loading: false, data: null, error: e.message });
    }
  };

  return (
    <ActionCard icon={icon} title={title} description={description} endpoint={endpoint} delay={delay}>
      <div className="flex gap-2">
        <Input
          placeholder="Transaction ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <Button variant="outline" onClick={run} disabled={!id || state.loading} className="shrink-0">
          {state.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : buttonLabel}
        </Button>
      </div>
      <AnimatePresence>
        {(state.data || state.error) && (
          <motion.pre
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 max-h-52 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-3 font-mono text-[11px] leading-relaxed text-slate-600"
          >
            {state.error ? `Error: ${state.error}` : JSON.stringify(state.data, null, 2)}
          </motion.pre>
        )}
      </AnimatePresence>
    </ActionCard>
  );
}
