import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Sparkles, Loader2 } from "lucide-react";
import ActionCard from "./ActionCard";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import MarkdownMessage from "@/components/ui/MarkdownMessage";
import { fraudApi } from "@/services/fraudApi";

export default function LlmCard() {
  const [id, setId] = useState("");
  const [state, setState] = useState({ loading: false, data: null, error: null });

  const generate = async () => {
    if (!id) return;
    setState({ loading: true, data: null, error: null });
    try {
      const data = await fraudApi.getLlmExplanation(id);
      setState({ loading: false, data, error: null });
    } catch (e) {
      setState({ loading: false, data: null, error: e.message });
    }
  };

  const explanation = state.data?.explanation;
  const notice = state.error || state.data?.error;
  const show = explanation || notice;

  return (
    <ActionCard
      icon={Bot}
      title="AI Explanation"
      description="Natural-language fraud reasoning via Gemini"
    >
      <div className="flex gap-2">
        <Input
          placeholder="Transaction ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && generate()}
        />
        <Button onClick={generate} disabled={!id || state.loading} className="shrink-0">
          {state.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          Generate
        </Button>
      </div>

      <AnimatePresence>
        {show && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 rounded-xl border border-primary-100 bg-primary-50/60 p-4"
          >
            <div className="mb-3 flex items-center gap-2 text-xs font-semibold text-primary-700">
              <Bot className="h-4 w-4" /> AI Response
            </div>
            {explanation ? (
              <MarkdownMessage content={explanation} />
            ) : (
              <p className="text-sm text-slate-600">{notice}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </ActionCard>
  );
}
