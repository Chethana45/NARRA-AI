import React from "react";
import { Cpu, GitBranch } from "lucide-react";

const Models: React.FC = () => {
  return (
    <section className="mx-auto mt-12 max-w-7xl px-6">
      <div className="rounded-2xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-6">
        <h3 className="text-lg font-semibold text-white">POWERED BY GENERATIVE AI</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-white/6 p-4">
            <div className="text-sm font-semibold text-white">VISION AI</div>
            <div className="mt-2 text-sm text-slate-400">BLIP — Understands your uploaded image</div>
          </div>
          <div className="rounded-xl border border-white/6 p-4">
            <div className="text-sm font-semibold text-white">GENERATIVE AI</div>
            <div className="mt-2 text-sm text-slate-400">FLAN-T5 — Transforms visual context into narrative</div>
          </div>
          <div className="rounded-xl border border-white/6 p-4">
            <div className="text-sm font-semibold text-white">VOICE AI</div>
            <div className="mt-2 text-sm text-slate-400">Text-to-Speech — Brings the generated story to life</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Models;
