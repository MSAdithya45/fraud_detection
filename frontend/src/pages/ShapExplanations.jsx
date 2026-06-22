import { Microscope, BarChart3 } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import EmptyState from "@/components/ui/EmptyState";
import ShapImportanceChart from "@/components/charts/ShapImportanceChart";
import ShapByIdCard from "@/components/actions/ShapByIdCard";
import { useShapImportance } from "@/hooks/useFraudData";

export default function ShapExplanations() {
  const shap = useShapImportance(12);

  return (
    <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
      <GlassCard>
        <div className="mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary-600" />
          <div>
            <h3 className="font-semibold text-slate-900">Global Feature Importance</h3>
            <p className="text-xs text-slate-400">Mean absolute SHAP impact across all transactions</p>
          </div>
        </div>
        {shap.isLoading ? (
          <EmptyState title="Loading…" />
        ) : shap.data?.length ? (
          <ShapImportanceChart data={shap.data} />
        ) : (
          <EmptyState title="No SHAP data yet" hint="Score transactions to populate explanations." />
        )}
      </GlassCard>

      <GlassCard>
        <div className="mb-4 flex items-center gap-2">
          <Microscope className="h-5 w-5 text-primary-600" />
          <div>
            <h3 className="font-semibold text-slate-900">Individual Explanation</h3>
            <p className="text-xs text-slate-400">Feature drivers for a single transaction</p>
          </div>
        </div>
        <ShapByIdCard />
      </GlassCard>
    </div>
  );
}
