import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2 } from "lucide-react";
import ActionCard from "./ActionCard";
import Button from "@/components/ui/Button";

/** One-click action card that fetches a collection and shows a count. */
export default function FetchAllCard({
  icon,
  title,
  description,
  endpoint,
  fetcher,
  buttonLabel,
  delay = 0,
}) {
  const [state, setState] = useState({ loading: false, data: null, error: null });

  const run = async () => {
    setState({ loading: true, data: null, error: null });
    try {
      const data = await fetcher();
      setState({ loading: false, data, error: null });
    } catch (e) {
      setState({ loading: false, data: null, error: e.message });
    }
  };

  const count = Array.isArray(state.data) ? state.data.length : null;

  return (
    <ActionCard icon={icon} title={title} description={description} endpoint={endpoint} delay={delay}>
      <Button variant="outline" onClick={run} disabled={state.loading} className="w-full">
        {state.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : buttonLabel}
      </Button>
      <AnimatePresence>
        {(state.data || state.error) && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 text-sm"
          >
            {state.error ? (
              <p className="text-slate-500">{state.error}</p>
            ) : (
              <p className="font-medium text-primary-700">
                Retrieved {count ?? "—"} record{count === 1 ? "" : "s"}
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </ActionCard>
  );
}
