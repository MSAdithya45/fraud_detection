import { PieChart, Sparkles } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import EmptyState from "@/components/ui/EmptyState";
import KpiGrid from "@/components/dashboard/KpiGrid";
import RiskDonutChart from "@/components/charts/RiskDonutChart";
import ShapImportanceChart from "@/components/charts/ShapImportanceChart";
import QuickActions from "@/components/dashboard/QuickActions";
import ApiStatus from "@/components/dashboard/ApiStatus";
import TransactionsTable from "@/components/tables/TransactionsTable";
import { useDashboardStats, useShapImportance } from "@/hooks/useFraudData";

function CardHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="mb-4 flex items-center gap-2">
      <Icon className="h-5 w-5 text-primary-600" />
      <div>
        <h3 className="font-semibold text-slate-900">{title}</h3>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { rows, stats, isLoading, isError, error } = useDashboardStats();
  const shap = useShapImportance(10);
  const hasData = rows.length > 0;

  return (
    <div className="space-y-5">
      <KpiGrid stats={stats} loading={isLoading} />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <GlassCard>
          <CardHeader icon={PieChart} title="Risk Breakdown" subtitle="By severity bucket" />
          {hasData ? (
            <RiskDonutChart distribution={stats.distribution} />
          ) : (
            <EmptyState title="No data" hint="Awaiting scored transactions." />
          )}
        </GlassCard>

        <GlassCard className="xl:col-span-2">
          <CardHeader icon={Sparkles} title="Top Fraud Drivers" subtitle="Global SHAP feature importance" />
          {shap.isLoading ? (
            <EmptyState title="Loading SHAP…" />
          ) : shap.data?.length ? (
            <ShapImportanceChart data={shap.data} />
          ) : (
            <EmptyState title="No SHAP explanations yet" hint="SHAP rows are generated as transactions are scored." />
          )}
        </GlassCard>
      </div>

      <TransactionsTable rows={rows} loading={isLoading} error={isError ? error : null} />

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <ApiStatus />
        <div className="lg:col-span-2">
          <QuickActions />
        </div>
      </div>
    </div>
  );
}
