// These reusable primitives keep visual behavior consistent across every page.
import { LoaderCircle } from "lucide-react";
import type { ButtonHTMLAttributes, PropsWithChildren } from "react";
export function Button({ className = "", children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) { return <button className={`btn-primary ${className}`} {...props}>{children}</button>; }
export function Card({ className = "", children }: PropsWithChildren<{ className?: string }>) { return <section className={`card ${className}`}>{children}</section>; }
export function Loading({ label = "Loading" }: { label?: string }) { return <div className="flex min-h-40 items-center justify-center gap-2 text-slate-400"><LoaderCircle className="animate-spin" size={20} />{label}…</div>; }
export function Empty({ children }: PropsWithChildren) { return <div className="rounded-xl border border-dashed border-emerald-200 bg-emerald-50/40 p-8 text-center text-sm text-slate-500">{children}</div>; }
