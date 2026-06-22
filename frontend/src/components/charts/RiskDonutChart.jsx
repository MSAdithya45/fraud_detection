import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import ChartTooltip from "./ChartTooltip";

// Monochromatic blue: lighter = lower risk, darker = higher risk.
const COLORS = { Low: "#bfdbfe", Medium: "#60a5fa", High: "#1d4ed8" };

export default function RiskDonutChart({ distribution = [] }) {
  const total = distribution.reduce((s, d) => s + d.value, 0);

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={230}>
        <PieChart>
          <Tooltip content={<ChartTooltip />} />
          <Pie
            data={distribution}
            dataKey="value"
            nameKey="name"
            innerRadius={62}
            outerRadius={92}
            paddingAngle={3}
            stroke="none"
          >
            {distribution.map((d) => (
              <Cell key={d.name} fill={COLORS[d.name] || "#93c5fd"} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-2xl font-bold text-slate-900">
          {total.toLocaleString("en-US")}
        </p>
        <p className="text-xs text-slate-400">Scored</p>
      </div>
      <div className="mt-2 flex flex-wrap justify-center gap-4">
        {distribution.map((d) => (
          <div key={d.name} className="flex items-center gap-2 text-xs text-slate-600">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ background: COLORS[d.name] }}
            />
            {d.name} Risk
          </div>
        ))}
      </div>
    </div>
  );
}
