import React from "react";
import { motion } from "framer-motion";
import { CheckCircle, Loader2, XCircle } from "lucide-react";

export type StepStatus = "pending" | "processing" | "complete" | "error";

const statusBadge = (status: StepStatus) => {
  switch (status) {
    case "pending":
      return <div className="text-slate-400">Pending</div>;
    case "processing":
      return (
        <div className="flex items-center gap-2 text-sky-300">
          <Loader2 className="animate-spin h-4 w-4" /> Processing
        </div>
      );
    case "complete":
      return (
        <div className="flex items-center gap-2 text-emerald-400">
          <CheckCircle className="h-4 w-4" /> Complete
        </div>
      );
    case "error":
      return (
        <div className="flex items-center gap-2 text-rose-400">
          <XCircle className="h-4 w-4" /> Error
        </div>
      );
  }
};

const Pipeline: React.FC<{ steps: Array<{ id: string; label: string; status: StepStatus }> }> = ({ steps }) => {
  return (
    <div className="space-y-3">
      {steps.map((s, idx) => (
        <motion.div
          key={s.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.04 }}
          className="flex items-center justify-between gap-4 rounded-xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-4"
        >
          <div>
            <div className="text-sm font-semibold text-white">{s.label}</div>
            <div className="text-xs text-slate-400">{s.id}</div>
          </div>
          <div>{statusBadge(s.status)}</div>
        </motion.div>
      ))}
    </div>
  );
};

export default Pipeline;
