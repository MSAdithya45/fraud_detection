import { apiClient } from "./apiClient";

/**
 * Typed wrappers around the FastAPI backend.
 * Endpoints that exist server-side:
 *   GET  /transactions
 *   GET  /transaction/{id}
 *   GET  /shap
 *   GET  /shap/{id}
 *   GET  /llm/{id}
 *   POST /predict   (multipart file upload)
 */
export const fraudApi = {
  getTransactions: () => apiClient.get("/transactions").then((r) => r.data),

  getTransaction: (id) =>
    apiClient.get(`/transaction/${id}`).then((r) => r.data),

  getAllShap: () => apiClient.get("/shap").then((r) => r.data),

  getTransactionShap: (id) =>
    apiClient.get(`/shap/${id}`).then((r) => r.data),

  getLlmExplanation: (id) =>
    apiClient.get(`/llm/${id}`).then((r) => r.data),

  getDrift: (severity) =>
    apiClient.get(`/drift/${severity}`).then((r) => r.data),

  predictCsv: (file, onUploadProgress) => {
    const form = new FormData();
    form.append("file", file);
    return apiClient
      .post("/predict", form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress,
      })
      .then((r) => r.data);
  },
};
