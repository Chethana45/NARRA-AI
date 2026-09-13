import React from "react";
import { motion } from "framer-motion";
import { Sparkles, Camera, Book, Headphones } from "lucide-react";


const GlassCard: React.FC<{ title: string; icon?: React.ReactNode; subtitle?: string; colorFrom?: string; colorTo?: string }> = ({ title, icon, subtitle, colorFrom = '#7C3AED', colorTo = '#60A5FA' }) => {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="rounded-2xl bg-white/6 p-4 shadow-xl backdrop-blur-sm border border-white/6">
      <div className="flex items-start gap-4">
        <div className="rounded-lg p-3" style={{ background: `linear-gradient(135deg, ${colorFrom}, ${colorTo})` }}>
          {icon}
        </div>
        <div>
          <div className="text-sm font-semibold text-white">{title}</div>
          {subtitle ? <div className="text-xs text-white/80">{subtitle}</div> : null}
        </div>
      </div>
    </motion.div>
  );
};

const Hero: React.FC<{ onCreate?: () => void; onHow?: () => void; onUploadClick?: () => void; onReadStory?: () => void; onListen?: () => void; storyExists?: boolean; audioExists?: boolean }> = ({ onCreate, onHow, onUploadClick, onReadStory, onListen, storyExists, audioExists }) => {
  return (
    <section className="relative mx-auto mt-6 w-full max-w-6xl px-6">
      {/* Decorative background blobs */}
      <div className="pointer-events-none absolute -inset-y-16 -left-20 -z-10 hidden md:block">
        <div className="absolute left-24 top-12 h-72 w-72 rounded-full bg-gradient-to-br from-[#7C3AED] via-[#5B21B6] to-[#2563EB] opacity-40 blur-3xl" />
        <div className="absolute left-64 top-40 h-48 w-48 rounded-full bg-gradient-to-br from-[#FF7AB6] via-[#7C3AED] to-[#60A5FA] opacity-30 blur-2xl" />
      </div>

      <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
        <div className="z-10">
          <div className="inline-flex items-center gap-3 rounded-full bg-gradient-to-r from-[#FF7AB6]/30 to-[#60A5FA]/20 px-3 py-1 text-sm font-semibold text-white">
            <Sparkles className="h-4 w-4 text-yellow-200" /> CREATIVE AI STORYTELLING
          </div>

          <h1 className="mt-6 max-w-xl text-5xl font-extrabold leading-tight text-white md:text-6xl">
            Turn Moments
            <br />
            <span className="bg-gradient-to-r from-[#60A5FA] via-[#7C3AED] to-[#FF7AB6] bg-clip-text text-transparent">Into Stories.</span>
          </h1>

          <p className="mt-4 max-w-lg text-lg text-white/80">
            NARRA.AI understands your photo, crafts a vivid caption and story, and brings it to life with an AI narration — like a digital memory made cinematic.
          </p>

          <div className="mt-6 flex gap-4">
            <button onClick={onCreate} className="rounded-full bg-gradient-to-r from-[#7C3AED] to-[#FF7AB6] px-6 py-3 text-lg font-bold text-white shadow-xl hover:translate-y-[-2px] transition-transform">
              Create Your Story ✨
            </button>
            {onHow ? (
              <button onClick={onHow} className="rounded-full border border-white/20 px-5 py-3 font-semibold text-white/90 hover:bg-white/5 transition">
                How it Works
              </button>
            ) : null}
          </div>

          {/* small doodles under CTA */}
          <div className="mt-6 flex items-center gap-4">
            <button onClick={onUploadClick} className="flex items-center gap-2 rounded-full bg-white/5 px-3 py-2 text-xs text-white/80 hover:bg-white/8 transition" aria-label="Upload a photo">
              <Camera className="h-4 w-4 text-white/90" /> Upload a photo
            </button>
            <button onClick={onReadStory} disabled={!storyExists} className={`flex items-center gap-2 rounded-full px-3 py-2 text-xs ${storyExists ? 'bg-white/5 text-white/90 hover:bg-white/8' : 'bg-white/3 text-white/40 cursor-not-allowed'}`} aria-label="Read the story">
              <Book className="h-4 w-4 text-white/90" /> Read the story
            </button>
            <button onClick={onListen} disabled={!audioExists} className={`flex items-center gap-2 rounded-full px-3 py-2 text-xs ${audioExists ? 'bg-white/5 text-white/90 hover:bg-white/8' : 'bg-white/3 text-white/40 cursor-not-allowed'}`} aria-label="Listen">
              <Headphones className="h-4 w-4 text-white/90" /> Listen
            </button>
          </div>
        </div>

        {/* Visual collage */}
        <div className="relative z-10 flex justify-center">
          <div className="relative flex h-[420px] w-full max-w-xl items-center justify-center">
            {/* Decorative gradient blobs */}
            <div className="absolute -left-28 -top-6 h-56 w-56 rounded-full bg-gradient-to-br from-[#7C3AED] to-[#60A5FA] opacity-40 blur-3xl" />
            <div className="absolute right-[-20px] top-12 h-44 w-44 rounded-full bg-gradient-to-br from-[#FF7AB6] to-[#7C3AED] opacity-30 blur-2xl" />

            {/* Glass pipeline cards stacked */}
            <div className="absolute left-0 top-6 w-48">
                          <GlassCard title="Upload Image" icon={<div className="text-2xl">📷</div>} subtitle="Drop your memory" colorFrom="#7C3AED" colorTo="#60A5FA" />
            </div>

            <div className="absolute left-16 top-40 w-56 transform rotate-2">
                          <GlassCard title="AI Caption" icon={<div className="text-2xl">✨</div>} subtitle='"Golden hour memories..."' colorFrom="#FF7AB6" colorTo="#7C3AED" />
            </div>

            <div className="absolute left-40 top-24 w-60 transform -rotate-3">
                          <GlassCard title="AI Story" icon={<div className="text-2xl">📖</div>} subtitle='"A moment worth remembering..."' colorFrom="#60A5FA" colorTo="#22D3EE" />
            </div>

            <div className="absolute left-56 top-56 w-44 transform rotate-1">
                          <GlassCard title="Narration" icon={<div className="text-2xl">🎧</div>} subtitle="Ready to listen" colorFrom="#A855F7" colorTo="#EC4899" />
            </div>

            {/* Decorative connectors */}
            <svg className="absolute inset-0 h-full w-full" viewBox="0 0 600 420" fill="none" preserveAspectRatio="none">
                          <path d="M120 120 C 200 160, 260 140, 320 200" stroke="#60A5FA" strokeWidth="2" strokeDasharray="6 6" opacity="0.6" />
                          <path d="M200 200 C 260 240, 340 220, 420 260" stroke="#FF7AB6" strokeWidth="2" strokeDasharray="6 6" opacity="0.6" />
            </svg>

            {/* Floating small sparkles */}
            <div className="absolute right-6 top-2">✦</div>
            <div className="absolute right-14 top-12">★</div>
          </div>
        </div>
      </div>

      {/* subtle border/edge glow */}
      <div className="pointer-events-none absolute inset-0 -z-20 bg-gradient-to-b from-transparent via-transparent to-black/5" />
    </section>
  );
};

export default Hero;

