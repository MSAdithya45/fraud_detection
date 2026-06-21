import { CreditCard, ShieldAlert, Percent, Gauge } from "lucide-react";
import KpiCard from "./KpiCard";

export default function KpiGrid({ stats, loading }) {
  const s = stats || {};
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <KpiCard icon={CreditCard} label="Total Transactions" value={s.total} loading={loading} delay={0} />
      <KpiCard icon={ShieldAlert} label="Fraud Detected" value={s.fraud} loading={loading} delay={0.05} />
      <KpiCard icon={Percent} label="Fraud Rate" value={s.fraudRate} decimals={1} suffix="%" loading={loading} delay={0.1} />
      <KpiCard icon={Gauge} label="Avg Risk Score" value={s.avgScore} decimals={1} suffix="/100" loading={loading} delay={0.15} />
    </div>
  );
}
