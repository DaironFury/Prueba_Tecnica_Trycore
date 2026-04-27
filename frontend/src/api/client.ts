import axios, { AxiosError } from "axios";

import type { ErrorResponse } from "@/types/api.types";

/**
 * Axios instance shared across the application.
 *
 * The base URL is `/api/v1`, a relative path. In development the Vite
 * proxy forwards it to the backend, in production nginx does the same.
 * The application code never references absolute URLs, ports or service
 * names — those concerns belong to the surrounding infrastructure.
 */
export const apiClient = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15_000,
});

export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
    public readonly field: string | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response?.data?.error) {
      const { code, message, field } = error.response.data.error;
      return Promise.reject(new ApiError(code, message, error.response.status, field));
    }
    return Promise.reject(
      new ApiError(
        "NETWORK_ERROR",
        error.message ?? "Network error",
        error.response?.status ?? 0,
      ),
    );
  },
);
