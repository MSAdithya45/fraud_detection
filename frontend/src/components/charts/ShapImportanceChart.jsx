import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import ChartTooltip from "./ChartTooltip";

/** Global feature importance aggregated from real SHAP rows. */
export default function ShapImportanceChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(260, data.length * 30)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
      >
        <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis
          type="category"
          dataKey="feature"
          width={110}
          tick={{ fill: "#475569", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(37,99,235,0.06)" }} />
        <Bar dataKey="importance" name="Mean |impact|" fill="#2563eb" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
