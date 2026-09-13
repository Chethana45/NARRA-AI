import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Studio from "./components/Studio";
import Pipeline, { StepStatus } from "./components/Pipeline";
import Results from "./components/Results";
import Models from "./components/Models";
import HowItWorks from "./components/HowItWorks";
import Features from "./components/Features";
import Footer from "./components/Footer";

const apiBase = "http://localhost:8000";

const initialSteps = [
  { id: "uploaded", label: "Upload", status: "pending" as StepStatus },
  { id: "understand", label: "Understand", status: "pending" as StepStatus },
  { id: "create", label: "Create", status: "pending" as StepStatus },
  { id: "listen", label: "Listen", status: "pending" as StepStatus },
];

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [style, setStyle] = useState<string>("Cinematic");
  const [context, setContext] = useState<string>("");
  const [caption, setCaption] = useState<string>("");
  const [story, setStory] = useState<string>("");
  const [audioUrl, setAudioUrl] = useState<string>("");
  const [generating, setGenerating] = useState<boolean>(false);
  const [steps, setSteps] = useState(initialSteps);
  const [mode, setMode] = useState<string>("");
  const [visualAnalysis, setVisualAnalysis] = useState<any>(null);
  const [researchResult, setResearchResult] = useState<any>(null);

  // Refs for sections and uploader
  const heroRef = useRef<HTMLElement | null>(null);
  const studioRef = useRef<HTMLElement | null>(null);
  const howRef = useRef<HTMLElement | null>(null);
  const storyRef = useRef<HTMLDivElement | null>(null);
  const audioRef = useRef<HTMLDivElement | null>(null);

  // Will be set by Studio to open the file dialog
  const openUploaderRef = useRef<(() => void) | null>(null);

  const scrollToElement = (el?: HTMLElement | null) => {
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  const onCreateClick = () => scrollToElement(studioRef.current);
  const onHomeClick = () => scrollToElement(heroRef.current);
  const onHowClick = () => scrollToElement(howRef.current);
  const onReadStoryClick = () => {
    if (story) scrollToElement(storyRef.current);
  };
  const onListenClick = () => {
    if (audioUrl) scrollToElement(audioRef.current);
  };

  const registerOpenUploader = (fn: () => void) => {
    openUploaderRef.current = fn;
  };

  const triggerOpenUploader = () => {
    if (openUploaderRef.current) openUploaderRef.current();
  };

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const updatePreview = (f: File) => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
    setSteps((s) => s.map((st) => (st.id === "uploaded" ? { ...st, status: "complete" } : st)));
  };

  const removeImage = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl("");
    setCaption("");
    setStory("");
    setAudioUrl("");
    setSteps(initialSteps);
  };

  const setStepStatus = (id: string, status: StepStatus) => {
    setSteps((s) => s.map((st) => (st.id === id ? { ...st, status } : st)));
  };

  const handleGenerate = async () => {
    if (!file) {
      toast.error("Please upload an image first.");
      return;
    }
    setGenerating(true);
    setCaption("");
    setStory("");
    setAudioUrl("");
    setVisualAnalysis(null);
    setResearchResult(null);
    setMode("");

    // start pipeline
    setStepStatus("understand", "processing");
    setStepStatus("create", "pending");
    setStepStatus("listen", "pending");

    try {
      const formData = new FormData();
      formData.append("image", file);
      formData.append("style", style);
      formData.append("context", context);

      const resp = await axios.post(`${apiBase}/generate`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000,
      });

      setStepStatus("understand", "complete");

      const data = resp.data as {
        caption: string;
        story: string;
        audio_url?: string;
        warning?: string;
        mode?: string;
        visual_analysis?: any;
        research?: any;
      };

      if (data.mode) setMode(data.mode);
      if (data.visual_analysis) setVisualAnalysis(data.visual_analysis);
      if (data.research) setResearchResult(data.research);

      if (data.caption) {
        setCaption(data.caption);
        setStepStatus("create", "complete");
      } else {
        setStepStatus("create", "error");
      }

      if (data.story) {
        setStory(data.story);
      }

      if (data.audio_url) {
        setAudioUrl(`${apiBase}${data.audio_url}`);
        setStepStatus("listen", "complete");
      } else {
        if (data.warning) setStepStatus("listen", "error");
      }

      if (data.warning) {
        toast((t) => <div className="text-sm">{data.warning}</div>);
      } else {
        toast.success("Story generated successfully");
      }
    } catch (err: any) {
      console.error(err);
      setStepStatus("understand", "error");
      toast.error(err?.response?.data?.detail || "Unable to generate story. See console for details.");
    } finally {
      setGenerating(false);
    }
  };

  const copyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Copied to clipboard");
    } catch {
      toast.error("Unable to copy");
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top_left,_#0b1026_0%,_transparent_30%),_radial-gradient(ellipse_at_bottom_right,_#2b1052_0%,_transparent_30%),_linear-gradient(180deg,#020617_0%,#07021a_100%)] text-slate-100">
      <Toaster position="top-right" />
      <Navbar onCreate={onCreateClick} onHome={onHomeClick} onHow={onHowClick} />

      <main className="mx-auto w-full max-w-6xl px-6 pt-28 pb-20">
        <section ref={(el) => (heroRef.current = el)}>
          <Hero onCreate={onCreateClick} onHow={onHowClick} onUploadClick={triggerOpenUploader} onReadStory={onReadStoryClick} onListen={onListenClick} storyExists={!!story} audioExists={!!audioUrl} />
        </section>

        {/* Studio - centered large card */}
        <section ref={(el) => (studioRef.current = el)} className="mt-10">
          <div className="mx-auto rounded-3xl bg-gradient-to-b from-black/40 to-slate-900/40 p-6 shadow-xl ring-1 ring-white/6">
            <Studio file={file} previewUrl={previewUrl} onSelect={updatePreview} onRemove={removeImage} context={context} setContext={setContext} style={style} setStyle={setStyle} onGenerate={handleGenerate} generating={generating} registerOpenUploader={registerOpenUploader} />
          </div>
        </section>

        {/* Pipeline / How it works - 4 equal cards */}
        <section className="mt-12">
          <h3 className="text-xl font-semibold text-white">AI Pipeline</h3>
          <p className="mt-2 text-slate-400">Track each stage as the AI analyzes your image and produces a story and narration.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((s) => (
              <div key={s.id} className="rounded-xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5">
                <div className="text-sm font-semibold text-slate-300">{s.label}</div>
                <div className="mt-3 text-lg font-bold text-white">
                  {s.status === "pending" && "Pending"}
                  {s.status === "processing" && "Processing..."}
                  {s.status === "complete" && "Complete"}
                  {s.status === "error" && "Error"}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Results */}
        <section className="mt-12">
          <h3 className="text-xl font-semibold text-white">Your AI Story</h3>
          <p className="mt-2 text-slate-400">Results from the AI appear here after generation.</p>

          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            <div className="rounded-2xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5">
              <div className="text-sm font-semibold text-slate-400">AI Caption</div>
              <div className="mt-3 text-white text-lg">{caption || "—"}</div>
            </div>

            <div ref={(el) => (storyRef.current = el)} className="rounded-2xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5">
              <div className="text-sm font-semibold text-slate-400">AI Story</div>
              <div className="mt-3 max-h-60 overflow-auto text-slate-200 whitespace-pre-line">{story || "—"}</div>
            </div>

            <div ref={(el) => (audioRef.current = el)} className="rounded-2xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5">
              <div className="text-sm font-semibold text-slate-400">AI Narration</div>
              <div className="mt-3">
                {audioUrl ? (
                  <div>
                    <audio src={audioUrl} controls className="w-full" />
                    <a href={audioUrl} download className="mt-3 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-sky-400 to-violet-500 px-4 py-2 text-sm font-semibold text-slate-900">
                      Download Audio
                    </a>
                  </div>
                ) : (
                  <div className="text-slate-500">No audio yet</div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Visual Understanding + Research (grounding transparency) */}
        {visualAnalysis || researchResult ? (
          <section className="mt-12">
            <div className="flex items-center gap-3">
              <h3 className="text-xl font-semibold text-white">How NARRA Understood This</h3>
              {mode ? (
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${mode === "gemini" ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}>
                  {mode === "gemini" ? "✨ Gemini-powered analysis" : "⚙️ Local offline fallback"}
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-slate-400">Full transparency: what was actually observed in the image, what was reasonably inferred, and what verified facts (if any) were researched.</p>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              {visualAnalysis ? (
                <div className="rounded-2xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5">
                  <div className="text-sm font-semibold text-slate-400">Visual Analysis</div>
                  <div className="mt-2 text-white">{visualAnalysis.visual_summary}</div>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs">
                    {visualAnalysis.scene_type && visualAnalysis.scene_type !== "unknown" ? (
                      <span className="rounded-full bg-white/10 px-2 py-1 text-slate-300">Scene: {visualAnalysis.scene_type}</span>
                    ) : null}
                    {visualAnalysis.mood && visualAnalysis.mood !== "unknown" ? (
                      <span className="rounded-full bg-white/10 px-2 py-1 text-slate-300">Mood: {visualAnalysis.mood}</span>
                    ) : null}
                    {visualAnalysis.composition && visualAnalysis.composition !== "unknown" ? (
                      <span className="rounded-full bg-white/10 px-2 py-1 text-slate-300">Composition: {visualAnalysis.composition}</span>
                    ) : null}
                  </div>

                  {visualAnalysis.observed ? (
                    <div className="mt-4">
                      <div className="text-xs font-semibold uppercase tracking-wide text-emerald-300">Observed</div>
                      <ul className="mt-2 space-y-1 text-sm text-slate-300">
                        {Object.entries(visualAnalysis.observed)
                          .filter(([, v]: any) => Array.isArray(v) && v.length > 0)
                          .map(([key, values]: any) => (
                            <li key={key}>
                              <span className="text-slate-500">{key}: </span>
                              {values.join(", ")}
                            </li>
                          ))}
                        {Object.values(visualAnalysis.observed).every((v: any) => !Array.isArray(v) || v.length === 0) ? (
                          <li className="text-slate-500">Nothing specific detected.</li>
                        ) : null}
                      </ul>
                    </div>
                  ) : null}

                  {visualAnalysis.inferred && visualAnalysis.inferred.length > 0 ? (
                    <div className="mt-4">
                      <div className="text-xs font-semibold uppercase tracking-wide text-sky-300">Inferred (reasonable guess, not certain)</div>
                      <ul className="mt-2 list-disc pl-5 text-sm text-slate-300">
                        {visualAnalysis.inferred.map((item: string, i: number) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}

                  {visualAnalysis.unknown && visualAnalysis.unknown.length > 0 ? (
                    <div className="mt-4">
                      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Unknown / Not determinable</div>
                      <ul className="mt-2 list-disc pl-5 text-sm text-slate-500">
                        {visualAnalysis.unknown.map((item: string, i: number) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              ) : null}

              <div className="rounded-2xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5">
                <div className="text-sm font-semibold text-slate-400">Research</div>
                {researchResult ? (
                  researchResult.found ? (
                    <div className="mt-2">
                      <div className="text-white font-semibold">{researchResult.title}</div>
                      {researchResult.description ? <div className="text-sm text-slate-400">{researchResult.description}</div> : null}
                      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-300">
                        {(researchResult.verified_facts || []).map((f: string, i: number) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                      {researchResult.url ? (
                        <a href={researchResult.url} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sm text-sky-300 underline">
                          Source: {researchResult.source} ↗
                        </a>
                      ) : null}
                    </div>
                  ) : (
                    <div className="mt-2 text-sm text-amber-300">
                      No verified information found{researchResult.query ? ` for "${researchResult.query}"` : ""}. The story does not include invented facts about this.
                    </div>
                  )
                ) : (
                  <div className="mt-2 text-sm text-slate-500">
                    No context was provided for this image, so no research was performed. Add a name, place, or event in "Who or what is this about?" to enable fact-checked research.
                  </div>
                )}
              </div>
            </div>
          </section>
        ) : null}

        {/* Stories Made With NARRA - Example story cards */}
        <section className="mt-12">
          <h3 className="text-xl font-semibold text-white">Stories Made With NARRA</h3>
          <p className="mt-2 text-slate-400">A few examples crafted by our models.</p>

          <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-2xl overflow-hidden shadow-2xl transform hover:-translate-y-2 transition bg-gradient-to-br from-[#EDE7FF] to-[#D6CCFF] p-4">
              <div className="rounded-lg h-40 bg-gradient-to-br from-[#7C3AED] to-[#FF7AB6] shadow-inner flex items-center justify-center text-white text-2xl font-bold">🌄</div>
              <div className="mt-4">
                <div className="text-sm font-semibold text-slate-800">A Quiet Evening</div>
                <div className="text-xs text-slate-600">Natural</div>
                <p className="mt-2 text-slate-800">"Golden light settles over a peaceful evening..."</p>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <div className="rounded-full bg-gradient-to-r from-[#7C3AED] to-[#60A5FA] px-3 py-2 text-white font-semibold">▶︎ Listen</div>
                <div className="text-xs text-slate-600">2:14</div>
              </div>
            </div>

            <div className="rounded-2xl overflow-hidden shadow-2xl transform hover:-translate-y-2 transition bg-gradient-to-br from-[#FFF1EA] to-[#FFE8D6] p-4">
              <div className="rounded-lg h-40 bg-gradient-to-br from-[#FFE08A] to-[#FFC6C6] shadow-inner flex items-center justify-center text-white text-2xl font-bold">🐾</div>
              <div className="mt-4">
                <div className="text-sm font-semibold text-slate-800">A Little Adventure</div>
                <div className="text-xs text-slate-600">Funny</div>
                <p className="mt-2 text-slate-800">"One curious explorer was definitely not ready to go home..."</p>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <div className="rounded-full bg-gradient-to-r from-[#FF9A9E] to-[#FECBBA] px-3 py-2 text-white font-semibold">▶︎ Listen</div>
                <div className="text-xs text-slate-600">1:38</div>
              </div>
            </div>

            <div className="rounded-2xl overflow-hidden shadow-2xl transform hover:-translate-y-2 transition bg-gradient-to-br from-[#E6F8FF] to-[#D3F4FF] p-4">
              <div className="rounded-lg h-40 bg-gradient-to-br from-[#60A5FA] to-[#7C3AED] shadow-inner flex items-center justify-center text-white text-2xl font-bold">🎉</div>
              <div className="mt-4">
                <div className="text-sm font-semibold text-slate-800">A Night To Remember</div>
                <div className="text-xs text-slate-600">Storytelling</div>
                <p className="mt-2 text-slate-800">"Some memories deserve to become stories..."</p>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <div className="rounded-full bg-gradient-to-r from-[#7C3AED] to-[#FF7AB6] px-3 py-2 text-white font-semibold">▶︎ Listen</div>
                <div className="text-xs text-slate-600">3:02</div>
              </div>
            </div>
          </div>
        </section>

        {/* Technology / Models */}
        <section className="mt-12">
          <h3 className="text-xl font-semibold text-white">Powered by Generative AI</h3>
          <p className="mt-2 text-slate-400">Vision, generative language, and voice technologies behind NARRA.AI.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5 text-center">
              <div className="text-sm font-semibold text-slate-300">BLIP (Vision AI)</div>
              <div className="mt-2 text-white">Understands your uploaded image</div>
            </div>
            <div className="rounded-xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5 text-center">
              <div className="text-sm font-semibold text-slate-300">FLAN-T5 (Generative AI)</div>
              <div className="mt-2 text-white">Transforms visual context into narrative</div>
            </div>
            <div className="rounded-xl border border-white/6 bg-gradient-to-b from-black/30 to-slate-900/30 p-5 text-center">
              <div className="text-sm font-semibold text-slate-300">Text-to-Speech</div>
              <div className="mt-2 text-white">Brings the generated story to life</div>
            </div>
          </div>
        </section>

        {/* How it works & features stacked */}
        <section ref={(el) => (howRef.current = el)} className="mt-12 grid gap-6 lg:grid-cols-2">
          <HowItWorks />
          <Features />
        </section>
      </main>

      <Footer />
    </div>
  );
}
