// This service maps every available FastAPI route into small, reusable frontend functions.
import { api } from "./api";
import type { Analytics, Dashboard, Farm, Forecast, Prediction, PredictionResult, TokenResponse, User } from "../types/api";

export const authApi = {
  login: (payload: { email: string; password: string }) => api.post<TokenResponse>("/login", payload).then((r) => r.data),
  register: (payload: { email: string; password: string; full_name?: string }) => api.post<User>("/signup", payload).then((r) => r.data),
  profile: () => api.get<User>("/profile").then((r) => r.data)
};
export const farmApi = {
  list: () => api.get<Farm[]>("/farm").then((r) => r.data),
  create: (payload: { farm_name: string; latitude: number; longitude: number; crop?: string; area?: number }) => api.post<Farm>("/farm", payload).then((r) => r.data),
  update: (id: number, payload: Partial<Pick<Farm, "farm_name" | "latitude" | "longitude" | "crop" | "area">>) => api.put<Farm>(`/farm/${id}`, payload).then((r) => r.data),
  remove: (id: number) => api.delete(`/farm/${id}`)
};
export const predictionApi = {
  create: (payload: { lat: number; lon: number; start_date: string; end_date: string; farm_id?: number }) => api.post<PredictionResult>("/predict", payload).then((r) => r.data),
  list: () => api.get<Prediction[]>("/predictions").then((r) => r.data),
  get: (id: number) => api.get<Prediction>(`/prediction/${id}`).then((r) => r.data),
  remove: (id: number) => api.delete(`/prediction/${id}`),
  reportUrl: (id: number) => `${api.defaults.baseURL}/report/${id}`,
  upload: (file: File) => { const data = new FormData(); data.append("file", file); return api.post<Blob>("/upload", data, { headers: { "Content-Type": "multipart/form-data" }, responseType: "blob" }).then((r) => r.data); }
};
export const dataApi = {
  dashboard: () => api.get<Dashboard>("/dashboard").then((r) => r.data),
  analytics: () => api.get<Analytics>("/analytics").then((r) => r.data),
  forecast: (latitude: number, longitude: number) => api.get<Forecast>("/forecast", { params: { latitude, longitude } }).then((r) => r.data),
  train: (payload: { lat: number; lon: number; start_date: string; end_date: string }) => api.post<{ status: string }>("/train", payload).then((r) => r.data)
};
