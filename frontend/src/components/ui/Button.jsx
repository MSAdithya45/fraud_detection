import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

const variants = {
  primary: "bg-primary-600 text-white hover:bg-primary-700 shadow-sm",
  outline:
    "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-400",
  soft: "bg-primary-50 text-primary-700 hover:bg-primary-100",
  ghost: "text-slate-600 hover:bg-slate-100",
};

const sizes = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-6 text-base",
};

export default function Button({
  children,
  className,
  variant = "primary",
  size = "md",
  ...props
}) {
  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium",
        "transition-colors disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
}
