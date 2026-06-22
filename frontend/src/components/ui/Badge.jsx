import { cn } from "@/utils/cn";

// Monochromatic blue severity scale (intensity encodes risk).
const tones = {
  Low: "bg-primary-50 text-primary-700 border-primary-100",
  Medium: "bg-primary-100 text-primary-800 border-primary-200",
  High: "bg-primary-600 text-white border-primary-600",
  FRAUD: "bg-primary-600 text-white border-primary-600",
  LEGIT: "bg-slate-100 text-slate-600 border-slate-200",
  neutral: "bg-slate-100 text-slate-600 border-slate-200",
};

export default function Badge({ children, tone = "neutral", className }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        tones[tone] || tones.neutral,
        className
      )}
    >
      {children}
    </span>
  );
}
