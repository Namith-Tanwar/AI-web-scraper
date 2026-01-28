import { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleScrape() {
    setLoading(true);
    setResult("");

    try {
      const response = await fetch("http://127.0.0.1:8000/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url,
          parse_description: description,
        }),
      });

      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.log(error);
      setResult("Error connecting to backend");
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center p-8">

      <h1 className="text-3xl font-bold mb-6">
        AI Web Scraper
      </h1>

      <div className="w-full max-w-3xl space-y-4">

        <input
          className="w-full p-3 rounded bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-400"
          type="text"
          placeholder="Enter URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <textarea
          className="w-full p-3 rounded bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-400"
          placeholder="Describe what to extract"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <button
          onClick={handleScrape}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded font-medium transition disabled:opacity-50"
        >
          {loading ? "Scraping..." : "Scrape"}
        </button>

        <pre className="bg-slate-800 border border-slate-700 rounded p-4 text-sm overflow-x-auto whitespace-pre-wrap">
          {result}
        </pre>

      </div>
    </div>

  );

}

export default App;
