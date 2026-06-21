import {
  LayoutDashboard,
  ArrowLeftRight,
  ShieldAlert,
  Microscope,
  Bot,
  Radar,
} from "lucide-react";

export const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/predictions", label: "Fraud Predictions", icon: ShieldAlert },
  { to: "/shap", label: "SHAP Explanations", icon: Microscope },
  { to: "/llm", label: "LLM Explanations", icon: Bot },
  { to: "/drift", label: "Drift Analysis", icon: Radar },
  { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
];

export const pageMeta = {
  "/dashboard": { title: "Overview", crumb: "Dashboard" },
  "/transactions": { title: "Transactions", crumb: "Transactions" },
  "/predictions": { title: "Fraud Predictions", crumb: "Predict" },
  "/shap": { title: "SHAP Explanations", crumb: "Explainability" },
  "/llm": { title: "AI Explanations", crumb: "LLM" },
  "/drift": { title: "Drift Analysis", crumb: "Monitoring" },
};
