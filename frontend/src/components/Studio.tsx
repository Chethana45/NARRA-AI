import React, { useRef } from "react";
import { ImageIcon, Trash2, Pen } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  file: File | null;
  previewUrl: string;
  onSelect: (file: File) => void;
  onRemove: () => void;
  context: string;
  setContext: (v: string) => void;
}

const StyleButton: React.FC<{ name: string; emoji: string; color: string; selected: boolean; onClick: () => void }> = ({ name, emoji, color, selected, onClick }) => (
  <button onClick={onClick} className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-shadow ${selected ? "shadow-2xl ring-2 ring-offset-2" : "hover:shadow-lg"}`} style={{ background: selected ? color : "rgba(255,255,255,0.04)", color: selected ? "#050014" : "#f8fafc" }}>
    <div className="text-lg">{emoji}</div>
    <div className="text-left">
      <div className="text-sm font-semibold">{name}</div>
    </div>
  </button>
);

const Studio: React.FC<Props & { style: string; setStyle: (s: string) => void; onGenerate: () => void; generating: boolean; registerOpenUploader?: (fn: () => void) => void }> = ({ file, previewUrl, onSelect, onRemove, context, setContext, style, setStyle, onGenerate, generating, registerOpenUploader }) => {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleBrowse = () => inputRef.current?.click();

  React.useEffect(() => {
    if (registerOpenUploader) registerOpenUploader(handleBrowse);
  }, [registerOpenUploader]);

  return (
    <div id="studio" className="rounded-3xl bg-white/6 p-6 shadow-2xl backdrop-blur-md">
      <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        <div>
          <div className="rounded-2xl bg-white/90 p-6 shadow-xl">
            {!file ? (
              <motion.div whileHover={{ scale: 1.02 }} onClick={handleBrowse} className="flex h-72 cursor-pointer items-center justify-center gap-4 rounded-xl border-2 border-dashed border-white/20 bg-gradient-to-br from-white/80 to-white/70 p-6 text-center">
                <div>
                  <div className="inline-flex items-center justify-center rounded-full bg-gradient-to-br from-[#7C3AED] to-[#60A5FA] p-3 text-white">
                    <ImageIcon className="h-6 w-6" />
                  </div>
                  <div className="mt-4 text-2xl font-bold text-slate-900">Drop your memory here 📸</div>
                  <div className="mt-2 text-sm text-slate-700">JPG, PNG, WEBP — up to 8MB</div>
                </div>
              </motion.div>
            ) : (
              <div className="relative">
                <img src={previewUrl} alt="preview" className="h-72 w-full rounded-xl object-cover object-center" />
                <div className="absolute right-4 top-4 flex gap-2">
                  <button onClick={handleBrowse} className="rounded-full bg-white/80 p-2 text-slate-900 hover:opacity-90">
                    <Pen className="h-4 w-4" />
                  </button>
                  <button onClick={onRemove} className="rounded-full bg-rose-500 p-2 text-white hover:opacity-90">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}

            <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => e.target.files && onSelect(e.target.files[0])} />
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <StyleButton name="Natural" emoji="🌿" color="linear-gradient(90deg,#CFF0D6,#A6E6B9)" selected={style === "Natural"} onClick={() => setStyle("Natural")} />
            <StyleButton name="Funny" emoji="😂" color="linear-gradient(90deg,#FFE08A,#FFC6C6)" selected={style === "Funny"} onClick={() => setStyle("Funny")} />
            <StyleButton name="Cinematic" emoji="🎬" color="linear-gradient(90deg,#E6D1FF,#FFD6F0)" selected={style === "Cinematic"} onClick={() => setStyle("Cinematic")} />
            <StyleButton name="Emotional" emoji="💭" color="linear-gradient(90deg,#FFD9E8,#FFC1D9)" selected={style === "Emotional"} onClick={() => setStyle("Emotional")} />
            <StyleButton name="Informative" emoji="📖" color="linear-gradient(90deg,#D9E8FF,#BFD8FF)" selected={style === "Informative"} onClick={() => setStyle("Informative")} />
            <StyleButton name="Inspirational" emoji="✨" color="linear-gradient(90deg,#FFF3C4,#FFE08A)" selected={style === "Inspirational"} onClick={() => setStyle("Inspirational")} />
            <StyleButton name="Mysterious" emoji="🕵️" color="linear-gradient(90deg,#D6D9FF,#B9C0FF)" selected={style === "Mysterious"} onClick={() => setStyle("Mysterious")} />
          </div>
        </div>

        <div className="flex flex-col items-stretch justify-between">
          <div className="rounded-2xl bg-white/8 p-6 shadow-inner">
            <div className="text-sm font-semibold text-white/90">Story Options</div>
            <div className="mt-4 text-sm text-white/80">Choose a tone and press Generate to begin. The AI will analyze your image and create a caption, story, and audio narration.</div>

            <div className="mt-6">
              <label htmlFor="narra-context" className="text-sm font-semibold text-white/90">
                Who or what is this image about? <span className="font-normal text-white/50">(optional)</span>
              </label>
              <input
                id="narra-context"
                type="text"
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="e.g. A. R. Rahman, the Eiffel Tower, my sister's wedding..."
                maxLength={200}
                className="mt-2 w-full rounded-xl border border-white/15 bg-white/10 px-4 py-3 text-sm text-white placeholder-white/40 outline-none focus:border-white/40 focus:bg-white/15"
              />
              <div className="mt-1 text-xs text-white/50">
                NARRA never guesses identities from faces — tell it who/what this is and it will research real, verified facts to ground the story.
              </div>
            </div>

            <div className="mt-8 flex w-full items-center">
              <button onClick={onGenerate} disabled={generating} className={`flex-1 rounded-full px-6 py-4 text-lg font-bold text-white shadow-lg transition ${generating ? "bg-slate-500/80" : "bg-gradient-to-r from-[#7C3AED] to-[#FF7AB6] hover:scale-[1.02]"}`}>
                {generating ? "Creating your story..." : "✨ TURN THIS IMAGE INTO A STORY"}
              </button>
            </div>
          </div>

          <div className="mt-6 rounded-2xl bg-white/6 p-4 text-sm text-white/80">
            <div className="font-semibold">Quick tips</div>
            <ul className="mt-2 list-disc pl-5 text-sm text-white/80">
              <li>Use clear photos with a single central subject for best stories.</li>
              <li>Try different styles to vary mood and tone.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Studio;
