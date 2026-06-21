import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ShieldAlert, Microscope, Bot, ArrowLeftRight } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";

const actions = [
  { label: "Run Prediction", icon: ShieldAlert, to: "/predictions" },
  { label: "SHAP Explorer", icon: Microscope, to: "/shap" },
  { label: "AI Explanation", icon: Bot, to: "/llm" },
  { label: "Transactions", icon: ArrowLeftRight, to: "/transactions" },
];

export default function QuickActions() {
  const navigate = useNavigate();
  return (
    <GlassCard>
      <h3 className="mb-4 font-semibold text-slate-900">Quick Actions</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {actions.map((a, i) => (
          <motion.button
            key={a.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate(a.to)}
            className="flex flex-col items-center gap-2 rounded-xl border border-slate-200 bg-white p-4 text-center transition hover:border-primary-300 hover:bg-primary-50"
          >
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-primary-50 text-primary-600">
              <a.icon className="h-5 w-5" />
            </span>
            <span className="text-xs font-medium text-slate-600">{a.label}</span>
          </motion.button>
        ))}
      </div>
    </GlassCard>
  );
}
