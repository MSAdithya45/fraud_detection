export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs shadow-md">
      {label && <p className="mb-1 font-semibold text-slate-800">{label}</p>}
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-slate-600">
          <span
            className="h-2 w-2 rounded-full"
            style={{ background: p.color || p.fill }}
          />
          <span className="capitalize">{p.name}:</span>
          <span className="font-medium text-slate-900">
            {Number(p.value).toLocaleString("en-US", { maximumFractionDigits: 4 })}
          </span>
        </div>
      ))}
    </div>
  );
}
