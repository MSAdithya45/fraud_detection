import { cn } from "@/utils/cn";

export default function Input({ className, icon: Icon, ...props }) {
  return (
    <div className="relative w-full">
      {Icon && (
        <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      )}
      <input
        className={cn(
          "h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-800",
          "placeholder:text-slate-400 outline-none transition",
          "focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20",
          Icon && "pl-9",
          className
        )}
        {...props}
      />
    </div>
  );
}
