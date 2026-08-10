import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const STAGES = [
  { key: "pending", label: "Queue" },
  { key: "scraping", label: "Fetch" },
  { key: "parsing", label: "Extract" },
  { key: "done", label: "Done" },
];

function stageIndex(status) {
  const i = STAGES.findIndex((s) => s.key === status);
  return i === -1 ? 0 : i;
}

function PipelineIndicator({ status }) {
  const isError = status === "error";
  const currentIdx = stageIndex(status);

  return (
    <div className="flex items-center gap-0 mono text-xs">
      {STAGES.map((stage, i) => {
        const isActive = !isError && i === currentIdx;
        const isComplete = !isError && i < currentIdx;
        const isDoneStage = stage.key === "done" && status === "done";

        return (
          <div key={stage.key} className="flex items-center">
            <div className="flex flex-col items-center gap-2">
              <div
                className={[
                  "w-2.5 h-2.5 rounded-full transition-all duration-300",
                  isError && i === 0 ? "bg-[var(--error)]" : "",
                  isDoneStage || isComplete
                    ? "bg-[var(--signal)]"
                    : isActive
                    ? "bg-[var(--signal)] animate-pulse ring-4 ring-[var(--signal-dim)]"
                    : !isError
                    ? "bg-[var(--border)]"
                    : "bg-[var(--border)]",
                ].join(" ")}
              />
              <span
                className={
                  isActive || isComplete || isDoneStage
                    ? "text-[var(--text)]"
                    : "text-[var(--text-dim)]"
                }
              >
                {stage.label}
              </span>
            </div>
            {i < STAGES.length - 1 && (
              <div
                className={[
                  "h-px w-10 sm:w-16 mx-1 mb-5 transition-all duration-500",
                  i < currentIdx && !isError ? "bg-[var(--signal)]" : "bg-[var(--border)]",
                ].join(" ")}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function App() {
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("idle"); // idle | pending | scraping | parsing | done | error
  const [result, setResult] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const pollRef = useRef(null);

  useEffect(() => {
    return () => clearTimeout(pollRef.current);
  }, []);

  async function pollStatus(jobId) {
    try {
      const res = await fetch(`${API_URL}/status/${jobId}`);
      if (!res.ok) throw new Error("Job not found");
      const data = await res.json();

      setStatus(data.status);

      if (data.status === "done") {
        setResult(data.result);
        return;
      }
      if (data.status === "error") {
        setErrorMsg(data.error || "Something went wrong while processing this page.");
        return;
      }

      pollRef.current = setTimeout(() => pollStatus(jobId), 1500);
    } catch (err) {
      setStatus("error");
      setErrorMsg("Lost connection to the server while checking job status.");
    }
  }

  async function handleScrape() {
    if (!url.trim() || !description.trim()) return;

    clearTimeout(pollRef.current);
    setResult("");
    setErrorMsg("");
    setStatus("pending");

    try {
      const res = await fetch(`${API_URL}/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, parse_description: description }),
      });

      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();

      pollStatus(data.job_id);
    } catch (err) {
      setStatus("error");
      setErrorMsg("Couldn't reach the scraper service. Check the URL and try again.");
    }
  }

  const isRunning = ["pending", "scraping", "parsing"].includes(status);

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)", color: "var(--text)" }}>
      <div className="max-w-3xl mx-auto px-6 py-16">
        <div className="mb-10">
          <div className="mono text-xs tracking-widest uppercase mb-3" style={{ color: "var(--signal)" }}>
            fetch · chunk · extract
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">AI Web Scraper</h1>
          <p className="mt-2 text-sm" style={{ color: "var(--text-dim)" }}>
            Give it a page and describe what you want back. It scrapes the
            rendered DOM, chunks the content, and asks an LLM to return it
            in whatever shape you asked for.
          </p>
        </div>

        <div
          className="rounded-lg border p-6 space-y-4"
          style={{ background: "var(--bg-panel)", borderColor: "var(--border)" }}
        >
          <div>
            <label className="mono text-xs block mb-1.5" style={{ color: "var(--text-dim)" }}>
              URL
            </label>
            <input
              className="w-full px-3 py-2.5 rounded mono text-sm outline-none border transition-colors focus:border-[var(--signal)]"
              style={{ background: "var(--bg)", borderColor: "var(--border)", color: "var(--text)" }}
              type="text"
              placeholder="https://example.com/jobs"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isRunning}
            />
          </div>

          <div>
            <label className="mono text-xs block mb-1.5" style={{ color: "var(--text-dim)" }}>
              What do you want extracted?
            </label>
            <textarea
              className="w-full px-3 py-2.5 rounded text-sm outline-none border transition-colors focus:border-[var(--signal)] resize-none"
              style={{ background: "var(--bg)", borderColor: "var(--border)", color: "var(--text)" }}
              placeholder="e.g. job titles with their salary, as a table"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isRunning}
            />
          </div>

          <button
            onClick={handleScrape}
            disabled={isRunning || !url.trim() || !description.trim()}
            className="w-full py-2.5 rounded font-medium text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ background: "var(--signal)", color: "var(--bg)" }}
          >
            {isRunning ? "Working..." : "Run extraction"}
          </button>
        </div>

        {status !== "idle" && (
          <div className="mt-8 flex justify-center">
            <PipelineIndicator status={status} />
          </div>
        )}

        {status === "error" && (
          <div
            className="mt-6 rounded-lg border px-4 py-3 text-sm"
            style={{ borderColor: "var(--error)", color: "var(--error)", background: "#2a1815" }}
          >
            <span className="mono font-medium">error — </span>
            {errorMsg}
          </div>
        )}

        {status === "done" && (
          <div
            className="mt-6 rounded-lg border p-6 text-sm leading-relaxed markdown-result"
            style={{ background: "var(--bg-panel)", borderColor: "var(--border)" }}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
