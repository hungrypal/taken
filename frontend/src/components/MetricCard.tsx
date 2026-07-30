// This component displays dashboard KPIs with a consistent icon-and-value presentation.
import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { Card } from "./ui";
export function MetricCard({ title, value, icon: Icon, accent = "text-emerald-700" }: { title: string; value: string | number; icon: LucideIcon; accent?: string }) { return <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}><Card className="p-5"><div className="flex items-center justify-between"><div><p className="text-sm text-slate-500">{title}</p><p className="mt-2 text-2xl font-bold text-slate-900">{value}</p></div><div className={`rounded-xl bg-emerald-50 p-3 ${accent}`}><Icon size={22} /></div></div></Card></motion.div>; }
