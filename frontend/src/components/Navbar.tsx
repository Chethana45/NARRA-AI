import React from "react";
import { Sparkles, Menu } from "lucide-react";
import { motion } from "framer-motion";

const Navbar: React.FC<{ onCreate?: () => void; onHome?: () => void; onHow?: () => void }> = ({ onCreate, onHome, onHow }) => {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.45 }}
      className="backdrop-blur-md sticky top-4 z-40 mx-auto max-w-7xl px-6"
    >
      <div className="flex items-center justify-between gap-6 rounded-2xl border border-white/6 bg-gradient-to-r from-black/50 to-slate-900/40 p-3 shadow-glass">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-violet-500 p-2 text-white shadow-md">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-semibold tracking-wider text-slate-200">NARRA.AI</div>
            <div className="text-xs text-slate-400">Turn images into stories</div>
          </div>
        </div>

        <div className="hidden items-center gap-6 md:flex">
          <button onClick={onHome} className="text-slate-300 hover:text-white">Home</button>
          <button onClick={onCreate} className="text-slate-300 hover:text-white">Create</button>
          <button onClick={onHow} className="text-slate-300 hover:text-white">How it Works</button>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onCreate}
            className="rounded-full bg-gradient-to-r from-sky-400 to-violet-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow hover:scale-[1.02] transition"
          >
            Start Creating
          </button>
          <div className="md:hidden">
            <Menu className="h-6 w-6 text-slate-300" />
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
