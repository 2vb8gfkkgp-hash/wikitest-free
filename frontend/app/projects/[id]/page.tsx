"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet, apiSend } from "../../../lib/api";

interface Draft {
  id: number;
  content: string;
}

interface Source {
  id: number;
  url: string;
  title: string;
  publisher?: string;
  author?: string;
  published_date?: string;
  source_type: string;
  notes?: string;
  excerpts?: string;
  is_primary: boolean;
  is_historical: boolean;
}

interface Interview {
  id: number;
  person: string;
  role?: string;
  interview_date?: string;
  transcript?: string;
  extracted_quotes?: string;
}

interface Claim {
  id: number;
  text: string;
  category: string;
  claim_type?: string;
  status: string;
  confidence: number;
}

interface Checklist {
  id: number;
  right_of_reply: boolean;
  separate_fact_opinion: boolean;
  avoid_sensational: boolean;
  quote_integrity: boolean;
}

export default function ProjectPage({ params }: { params: { id: string } }) {
  const projectId = params.id;
  const [draft, setDraft] = useState<Draft | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [checklist, setChecklist] = useState<Checklist | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [aiResult, setAiResult] = useState("");
  const [tone, setTone] = useState("news");

  const loadAll = async () => {
    const [draftData, sourcesData, interviewsData, claimsData, checklistData] = await Promise.all([
      apiGet<Draft>(`/projects/${projectId}/draft`),
      apiGet<Source[]>(`/projects/${projectId}/sources`),
      apiGet<Interview[]>(`/projects/${projectId}/interviews`),
      apiGet<Claim[]>(`/projects/${projectId}/claims`),
      apiGet<Checklist>(`/projects/${projectId}/checklist`),
    ]);
    setDraft(draftData);
    setSources(sourcesData);
    setInterviews(interviewsData);
    setClaims(claimsData);
    setChecklist(checklistData);
  };

  useEffect(() => {
    loadAll();
  }, []);

  const updateDraft = async () => {
    if (!draft) return;
    const updated = await apiSend<Draft>(`/projects/${projectId}/draft`, "PUT", { content: draft.content });
    setDraft(updated);
  };

  const addSource = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
      url: (form.elements.namedItem("url") as HTMLInputElement).value,
      title: (form.elements.namedItem("title") as HTMLInputElement).value,
      publisher: (form.elements.namedItem("publisher") as HTMLInputElement).value || null,
      author: (form.elements.namedItem("author") as HTMLInputElement).value || null,
      published_date: (form.elements.namedItem("published_date") as HTMLInputElement).value || null,
      source_type: (form.elements.namedItem("source_type") as HTMLSelectElement).value,
      notes: (form.elements.namedItem("notes") as HTMLInputElement).value || null,
      excerpts: (form.elements.namedItem("excerpts") as HTMLInputElement).value || null,
      is_primary: (form.elements.namedItem("is_primary") as HTMLInputElement).checked,
      is_historical: (form.elements.namedItem("is_historical") as HTMLInputElement).checked,
    };
    await apiSend(`/projects/${projectId}/sources`, "POST", payload);
    form.reset();
    loadAll();
  };

  const addInterview = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
      person: (form.elements.namedItem("person") as HTMLInputElement).value,
      role: (form.elements.namedItem("role") as HTMLInputElement).value || null,
      interview_date: (form.elements.namedItem("interview_date") as HTMLInputElement).value || null,
      transcript: (form.elements.namedItem("transcript") as HTMLInputElement).value || null,
      extracted_quotes: (form.elements.namedItem("extracted_quotes") as HTMLInputElement).value || null,
    };
    await apiSend(`/projects/${projectId}/interviews`, "POST", payload);
    form.reset();
    loadAll();
  };

  const runExtraction = async () => {
    await apiSend(`/projects/${projectId}/extract-claims`, "POST");
    loadAll();
  };

  const runMatching = async () => {
    await apiSend(`/projects/${projectId}/match-claims`, "POST");
    loadAll();
  };

  const runSearch = async () => {
    const data = await apiGet<any>(`/search?query=${encodeURIComponent(searchQuery)}`);
    setSearchResults(data.results);
  };

  const importResult = async (result: any) => {
    await apiSend(`/projects/${projectId}/import-source`, "POST", {
      url: result.url,
      title: result.title,
      publisher: result.domain,
      author: null,
      published_date: result.published_date || null,
      source_type: "news",
      notes: result.snippet,
      excerpts: null,
      is_primary: false,
      is_historical: false,
    });
    loadAll();
  };

  const updateChecklist = async (field: keyof Checklist, value: boolean) => {
    if (!checklist) return;
    const updated = await apiSend<Checklist>(`/projects/${projectId}/checklist`, "PUT", {
      ...checklist,
      [field]: value,
    });
    setChecklist(updated);
  };

  const runAiTool = async (tool: string) => {
    if (!draft?.content) return;
    if (tool === "tone") {
      const response = await apiSend<any>(
        `/tools/tone?text=${encodeURIComponent(draft.content)}&tone=${tone}`,
        "POST",
      );
      setAiResult(response.result);
    } else if (tool === "clarity") {
      const response = await apiSend<any>(`/tools/clarity?text=${encodeURIComponent(draft.content)}`, "POST");
      setAiResult(response.result);
    } else if (tool === "headline") {
      const response = await apiSend<any>(`/tools/headline?text=${encodeURIComponent(draft.content)}`, "POST");
      setAiResult(`${response.headline}\n${response.subheading}`);
    } else {
      const response = await apiSend<any>(`/tools/structure?text=${encodeURIComponent(draft.content)}`, "POST");
      setAiResult(JSON.stringify(response.suggestions, null, 2));
    }
  };

  return (
    <main>
      <header>
        <div>
          <h1>Project {projectId}</h1>
          <p className="small">Track sources, claims, and ethics checks.</p>
        </div>
        <Link href={`/projects/${projectId}/report`}>View report →</Link>
      </header>

      <div className="card">
        <h2>Draft</h2>
        <textarea
          rows={6}
          value={draft?.content || ""}
          onChange={(e) => setDraft(draft ? { ...draft, content: e.target.value } : null)}
        />
        <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
          <button onClick={updateDraft}>Save draft</button>
          <button className="secondary" onClick={runExtraction}>
            Extract claims
          </button>
          <button className="secondary" onClick={runMatching}>
            Match sources
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Sources</h2>
        <form className="grid grid-2" onSubmit={addSource}>
          <div>
            <label>URL</label>
            <input name="url" required />
          </div>
          <div>
            <label>Title</label>
            <input name="title" required />
          </div>
          <div>
            <label>Publisher/domain</label>
            <input name="publisher" />
          </div>
          <div>
            <label>Author</label>
            <input name="author" />
          </div>
          <div>
            <label>Date</label>
            <input type="date" name="published_date" />
          </div>
          <div>
            <label>Type</label>
            <select name="source_type">
              <option value="news">news</option>
              <option value="report">report</option>
              <option value="study">study</option>
              <option value="blog">blog</option>
              <option value="interview">interview</option>
            </select>
          </div>
          <div>
            <label>Notes</label>
            <input name="notes" />
          </div>
          <div>
            <label>Excerpts</label>
            <input name="excerpts" />
          </div>
          <div>
            <label>
              <input type="checkbox" name="is_primary" /> Primary source
            </label>
          </div>
          <div>
            <label>
              <input type="checkbox" name="is_historical" /> Historical
            </label>
          </div>
          <button type="submit">Add source</button>
        </form>
        <div className="grid">
          {sources.map((source) => (
            <div className="card" key={source.id}>
              <h3>{source.title}</h3>
              <p className="small">{source.publisher}</p>
              <p className="small">{source.url}</p>
              {source.is_primary && <span className="badge">Primary</span>}
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>Interviews</h2>
        <form className="grid grid-2" onSubmit={addInterview}>
          <div>
            <label>Person</label>
            <input name="person" required />
          </div>
          <div>
            <label>Role</label>
            <input name="role" />
          </div>
          <div>
            <label>Date</label>
            <input type="date" name="interview_date" />
          </div>
          <div>
            <label>Transcript/notes</label>
            <input name="transcript" />
          </div>
          <div>
            <label>Extracted quotes</label>
            <input name="extracted_quotes" />
          </div>
          <button type="submit">Add interview</button>
        </form>
        <div className="grid">
          {interviews.map((interview) => (
            <div className="card" key={interview.id}>
              <h3>{interview.person}</h3>
              <p className="small">{interview.role}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>Claims</h2>
        <div className="grid">
          {claims.map((claim) => (
            <div className="card" key={claim.id}>
              <p>{claim.text}</p>
              <p className="small">
                {claim.category} • {claim.claim_type} • {claim.status} (confidence {claim.confidence.toFixed(2)})
              </p>
              <Link href={`/projects/${projectId}/claims/${claim.id}`}>View claim →</Link>
            </div>
          ))}
          {claims.length === 0 && <p className="small">No claims extracted yet.</p>}
        </div>
      </div>

      <div className="card">
        <h2>Ethical guardrails</h2>
        <div className="grid grid-2">
          <label>
            <input
              type="checkbox"
              checked={checklist?.right_of_reply || false}
              onChange={(e) => updateChecklist("right_of_reply", e.target.checked)}
            />
            Right of reply attempted
          </label>
          <label>
            <input
              type="checkbox"
              checked={checklist?.separate_fact_opinion || false}
              onChange={(e) => updateChecklist("separate_fact_opinion", e.target.checked)}
            />
            Separate fact vs opinion
          </label>
          <label>
            <input
              type="checkbox"
              checked={checklist?.avoid_sensational || false}
              onChange={(e) => updateChecklist("avoid_sensational", e.target.checked)}
            />
            Avoid sensational framing
          </label>
          <label>
            <input
              type="checkbox"
              checked={checklist?.quote_integrity || false}
              onChange={(e) => updateChecklist("quote_integrity", e.target.checked)}
            />
            Quotes linked to transcripts
          </label>
        </div>
      </div>

      <div className="card">
        <h2>Find sources for a claim</h2>
        <input
          placeholder="Search query"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button onClick={runSearch}>Search</button>
        <div className="grid">
          {searchResults.map((result) => (
            <div className="card" key={result.url}>
              <h3>{result.title}</h3>
              <p className="small">{result.domain}</p>
              <p className="small">{result.snippet}</p>
              <button className="secondary" onClick={() => importResult(result)}>
                Import source
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>AI writing tools (transparent)</h2>
        <p className="small">Tools only edit existing text and never add new facts.</p>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          <button onClick={() => runAiTool("clarity")}>Clarity pass</button>
          <div>
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option value="news">News</option>
              <option value="feature">Feature</option>
              <option value="opinion">Opinion</option>
              <option value="newsletter">Newsletter</option>
            </select>
            <button onClick={() => runAiTool("tone")}>Tone pass</button>
          </div>
          <button onClick={() => runAiTool("headline")}>Headline + subheading</button>
          <button onClick={() => runAiTool("structure")}>Structure tips</button>
        </div>
        <textarea rows={6} value={aiResult} readOnly />
      </div>
    </main>
  );
}
