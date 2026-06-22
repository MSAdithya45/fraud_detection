import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

/**
 * Solid, professional card surface (formerly glass).
 * Kept the export name to avoid churn across imports.
 */
export default function GlassCard({
  children,
  className,
  hover = false,
  delay = 0,
  ...props
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn("card p-5", hover && "card-hover", className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}
