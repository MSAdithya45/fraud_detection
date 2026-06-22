import GlassCard from "@/components/ui/GlassCard";
import AnimatedCounter from "@/components/ui/AnimatedCounter";

export default function KpiCard({
  icon: Icon,
  label,
  value,
  decimals = 0,
  suffix = "",
  text,
  loading = false,
  delay = 0,
}) {
  return (
    <GlassCard hover delay={delay}>
      <div className="flex items-center justify-between">
        <span className="grid h-11 w-11 place-items-center rounded-xl bg-primary-50 text-primary-600">
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <p className="mt-4 text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
        {loading ? (
          <span className="inline-block h-7 w-16 animate-pulse rounded bg-slate-100" />
        ) : text != null ? (
          text
        ) : (
          <AnimatedCounter value={value} decimals={decimals} suffix={suffix} />
        )}
      </p>
    </GlassCard>
  );
}
