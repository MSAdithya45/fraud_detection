import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/Dashboard";
import Transactions from "@/pages/Transactions";
import Predictions from "@/pages/Predictions";
import ShapExplanations from "@/pages/ShapExplanations";
import LlmExplanations from "@/pages/LlmExplanations";
import DriftAnalysis from "@/pages/DriftAnalysis";

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/shap" element={<ShapExplanations />} />
            <Route path="/llm" element={<LlmExplanations />} />
            <Route path="/drift" element={<DriftAnalysis />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
