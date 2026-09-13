import React from "react";

const HowItWorks: React.FC = () => {
  return (
    <section className="mx-auto mt-12 max-w-7xl px-6">
      <h3 className="text-lg font-semibold text-white">How it works</h3>
      <div className="mt-6 grid gap-6 md:grid-cols-4">
        <div className="rounded-2xl border border-white/6 p-6 text-center">
          <div className="text-3xl font-bold text-sky-400">01</div>
          <div className="mt-2 text-sm font-semibold text-white">Upload</div>
          <div className="mt-1 text-xs text-slate-400">Choose your image</div>
        </div>
        <div className="rounded-2xl border border-white/6 p-6 text-center">
          <div className="text-3xl font-bold text-indigo-400">02</div>
          <div className="mt-2 text-sm font-semibold text-white">Understand</div>
          <div className="mt-1 text-xs text-slate-400">Vision AI analyzes the scene</div>
        </div>
        <div className="rounded-2xl border border-white/6 p-6 text-center">
          <div className="text-3xl font-bold text-violet-400">03</div>
          <div className="mt-2 text-sm font-semibold text-white">Create</div>
          <div className="mt-1 text-xs text-slate-400">Generative AI writes your story</div>
        </div>
        <div className="rounded-2xl border border-white/6 p-6 text-center">
          <div className="text-3xl font-bold text-cyan-400">04</div>
          <div className="mt-2 text-sm font-semibold text-white">Listen</div>
          <div className="mt-1 text-xs text-slate-400">AI turns the story into narration</div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
