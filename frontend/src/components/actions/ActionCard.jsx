import GlassCard from "@/components/ui/GlassCard";

/** Shell for an endpoint action card: icon, title, description, method badge. */
export default function ActionCard({
  icon: Icon,
  title,
  description,
  method = "GET",
  endpoint,
  children,
  delay = 0,
}) {
  return (
    <GlassCard delay={delay} className="flex h-full flex-col">
      <div className="mb-3 flex items-start gap-3">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary-600">
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <h3 className="font-semibold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500">{description}</p>
        </div>
      </div>
      {endpoint && (
        <div className="mb-4">
          <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[10px] text-slate-500">
            {method} {endpoint}
          </span>
        </div>
      )}
      <div className="mt-auto">{children}</div>
    </GlassCard>
  );
}
