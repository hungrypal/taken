// This context offers lightweight accessible notifications without another state dependency.
import { createContext, useCallback, useContext, useState, type PropsWithChildren } from "react";
type Toast = { id: number; message: string; type: "success" | "error" };
const ToastContext = createContext<{ show: (message: string, type?: Toast["type"]) => void }>({ show: () => undefined });
export function ToastProvider({ children }: PropsWithChildren) { const [toasts, setToasts] = useState<Toast[]>([]); const show = useCallback((message: string, type: Toast["type"] = "success") => { const id = Date.now(); setToasts((current) => [...current, { id, message, type }]); window.setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), 3500); }, []); return <ToastContext.Provider value={{ show }}>{children}<div aria-live="polite" className="fixed right-4 top-4 z-[100] space-y-2">{toasts.map((toast) => <div key={toast.id} className={`rounded-lg px-4 py-3 text-sm shadow-lg ${toast.type === "error" ? "bg-red-600" : "bg-teal-600"}`}>{toast.message}</div>)}</div></ToastContext.Provider>; }
export const useToast = () => useContext(ToastContext);
