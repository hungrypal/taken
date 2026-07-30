// This entry point composes routing, caching, notifications, and global styles.
import "leaflet/dist/leaflet.css";
import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";

const client = new QueryClient({ defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } } });
createRoot(document.getElementById("root")!).render(
  <StrictMode><QueryClientProvider client={client}><ToastProvider><AuthProvider><BrowserRouter><App /></BrowserRouter></AuthProvider></ToastProvider></QueryClientProvider></StrictMode>
);
