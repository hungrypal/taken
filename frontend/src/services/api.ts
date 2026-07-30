// This Axios instance attaches tokens, refreshes expired sessions, and centralizes API failures.
import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL } from "../config/env";

export const api = axios.create({ baseURL: API_BASE_URL, timeout: 30_000, headers: { "Content-Type": "application/json" } });
let refreshPromise: Promise<string | null> | null = null;

const tokenStore = () => localStorage.getItem("terrascore.refresh_token") ? localStorage : sessionStorage;
const getAccessToken = () => localStorage.getItem("terrascore.access_token") ?? sessionStorage.getItem("terrascore.access_token");
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use((response) => response, async (error: AxiosError<{ detail?: string }>) => {
  const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
  if (error.response?.status !== 401 || !original || original._retry || original.url?.includes("/refresh")) return Promise.reject(error);
  original._retry = true;
  const refreshToken = localStorage.getItem("terrascore.refresh_token") ?? sessionStorage.getItem("terrascore.refresh_token");
  if (!refreshToken) { localStorage.removeItem("terrascore.access_token"); sessionStorage.removeItem("terrascore.access_token"); window.dispatchEvent(new Event("terrascore:logout")); return Promise.reject(error); }
  refreshPromise ??= api.post<{ access_token: string }>("/refresh", { refresh_token: refreshToken }).then(({ data }) => data.access_token).catch(() => null).finally(() => { refreshPromise = null; });
  const nextToken = await refreshPromise;
  if (!nextToken) { localStorage.removeItem("terrascore.access_token"); localStorage.removeItem("terrascore.refresh_token"); sessionStorage.removeItem("terrascore.access_token"); sessionStorage.removeItem("terrascore.refresh_token"); window.dispatchEvent(new Event("terrascore:logout")); return Promise.reject(error); }
  tokenStore().setItem("terrascore.access_token", nextToken);
  original.headers.Authorization = `Bearer ${nextToken}`;
  return api(original);
});

export const errorMessage = (error: unknown) => axios.isAxiosError(error) ? error.response?.data?.detail ?? "Network request failed." : "An unexpected error occurred.";
