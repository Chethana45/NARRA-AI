import React, { useRef, useEffect } from "react";
import { Copy, Download, Play, Pause, Volume2 } from "lucide-react";

const Results: React.FC<{
  imageUrl: string;
  caption: string;
  story: string;
  audioUrl: string;
  onCopy: (text: string) => void;
}> = ({ imageUrl, caption, story, audioUrl, onCopy }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = React.useState(false);
  const [current, setCurrent] = React.useState(0);
  const [duration, setDuration] = React.useState(0);
  const [volume, setVolume] = React.useState(0.9);

  useEffect(() => {
    if (!audioRef.current) return;
    audioRef.current.volume = volume;
    const el = audioRef.current;
    const onTime = () => setCurrent(el.currentTime);
    const onLoaded = () => setDuration(el.duration || 0);
    const onEnd = () => setPlaying(false);
    el.addEventListener("timeupdate", onTime);
    el.addEventListener("loadedmetadata", onLoaded);
    el.addEventListener("ended", onEnd);
    return () => {
      el.removeEventListener("timeupdate", onTime);
      el.removeEventListener("loadedmetadata", onLoaded);
      el.removeEventListener("ended", onEnd);
    };
  }, [audioUrl, volume]);

  const toggle = () => {
    if (!audioRef.current) return;
    if (playing) {
      audioRef.current.pause();
      setPlaying(false);
    } else {
      audioRef.current.play();
      setPlaying(true);
    }
  };

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-3">
      <div className="rounded-2xl p-4" style={{ background: "linear-gradient(135deg,#EDE7FF, #D6CCFF)" }}>
        <div className="text-sm font-semibold text-slate-700">AI Caption</div>
        <div className="mt-3 text-slate-900 text-lg font-medium">{caption || "—"}</div>
        <button onClick={() => onCopy(caption)} className="mt-4 rounded-md bg-white/90 px-3 py-2 text-sm font-semibold shadow">
          <Copy className="inline-block mr-2 h-4 w-4" /> Copy
        </button>
      </div>

      <div className="rounded-2xl p-4" style={{ background: "linear-gradient(135deg,#FFE7F0,#FFD6E8)" }}>
        <div className="text-sm font-semibold text-slate-700">Your Story</div>
        <div className="mt-3 max-h-60 overflow-auto text-slate-900 whitespace-pre-line">{story || "—"}</div>
        <button onClick={() => onCopy(story)} className="mt-4 rounded-md bg-white/90 px-3 py-2 text-sm font-semibold shadow">
          <Copy className="inline-block mr-2 h-4 w-4" /> Copy Story
        </button>
      </div>

      <div className="rounded-2xl p-4" style={{ background: "linear-gradient(135deg,#DFF6FF,#C3F0FF)" }}>
        <div className="text-sm font-semibold text-slate-700">AI Narration</div>
        <div className="mt-3 flex items-center gap-4">
          <button onClick={toggle} className="rounded-full bg-white p-3 text-slate-900 shadow">
            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <div className="flex-1">
            <div className="text-sm text-slate-800">{audioUrl ? "Narration ready" : "No audio"}</div>
            <div className="mt-3">
              {audioUrl ? <audio ref={audioRef} src={audioUrl} controls className="w-full rounded-md" /> : <div className="text-sm text-slate-700">Upload an image and generate to create narration.</div>}
            </div>
          </div>
        </div>
        {audioUrl ? (
          <a href={audioUrl} download className="mt-4 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-[#7C3AED] to-[#60A5FA] px-4 py-2 text-sm font-semibold text-white">
            <Download className="h-4 w-4" /> Download Audio
          </a>
        ) : null}
      </div>
    </div>
  );
};

export default Results;
