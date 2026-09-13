import React from "react";

const Footer: React.FC = () => {
  return (
    <footer className="mt-16 border-t border-white/6 py-8">
      <div className="mx-auto max-w-7xl px-6 text-center text-sm text-slate-400">
        <div className="font-semibold text-white">NARRA.AI</div>
        <div className="mt-1">Turn moments into stories.</div>
        <div className="mt-2">Built with Generative AI — React • FastAPI • Hugging Face • PyTorch</div>
      </div>
    </footer>
  );
};

export default Footer;
