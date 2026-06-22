import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.error ||
      error?.message ||
      "Request failed";
    return Promise.reject(new Error(message));
  }
);
