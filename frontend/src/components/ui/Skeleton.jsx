import { cn } from "@/utils/cn";

export default function Skeleton({ className }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-md bg-slate-100",
        "after:absolute after:inset-0 after:-translate-x-full",
        "after:bg-gradient-to-r after:from-transparent after:via-white/70 after:to-transparent",
        "after:animate-shimmer",
        className
      )}
    />
  );
}
