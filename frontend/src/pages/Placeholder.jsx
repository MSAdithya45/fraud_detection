import { Construction } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";

export default function Placeholder({ title = "Coming soon", note }) {
  return (
    <GlassCard className="grid place-items-center py-24 text-center">
      <div className="grid h-16 w-16 place-items-center rounded-2xl bg-primary-50 text-primary-600">
        <Construction className="h-7 w-7" />
      </div>
      <h2 className="mt-5 text-xl font-bold text-slate-900">{title}</h2>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        {note || "This module is part of the FraudLens roadmap and will light up here soon."}
      </p>
    </GlassCard>
  );
}
