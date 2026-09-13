import React from "react";

const Features: React.FC = () => {
  const items = [
    "AI Image Understanding",
    "Smart Caption Generation",
    "Creative Story Generation",
    "Multiple Story Styles",
    "AI Voice Narration",
    "Downloadable Audio",
  ];

  return (
    <section className="mx-auto mt-12 max-w-7xl px-6">
      <h3 className="text-lg font-semibold text-white">Features</h3>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {items.map((it) => (
          <div key={it} className="rounded-xl border border-white/6 p-4">
            <div className="text-sm font-semibold text-white">{it}</div>
            <div className="mt-1 text-xs text-slate-400">High quality</div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Features;
