"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "../../../../lib/api";

interface ReportItem {
  claim: { id: number; text: string; status: string };
  matches: { match_score: number; overlap?: string; source_id?: number; interview_id?: number }[];
  confidence_explanation: string;
}

export default function ReportPage({ params }: { params: { id: string } }) {
  const projectId = params.id;
  const [items, setItems] = useState<ReportItem[]>([]);
  const [markdown, setMarkdown] = useState("");
  const [jsonReport, setJsonReport] = useState("");

  useEffect(() => {
    const load = async () => {
      const report = await apiGet<{ items: ReportItem[] }>(`/projects/${projectId}/report`);
      const markdownData = await apiGet<{ markdown: string }>(`/projects/${projectId}/export/markdown`);
      const jsonData = await apiGet<{ json: string }>(`/projects/${projectId}/export/json`);
      setItems(report.items);
      setMarkdown(markdownData.markdown);
      setJsonReport(jsonData.json);
    };
    load();
  }, [projectId]);

  const copy = async (text: string) => {
    await navigator.clipboard.writeText(text);
  };

  return (
    <main>
      <header>
        <h1>Evidence report</h1>
        <Link href={`/projects/${projectId}`}>Back to project</Link>
      </header>

      <div className="card">
        {items.map((item) => (
          <div className="card" key={item.claim.id}>
            <h3>{item.claim.text}</h3>
            <p className="small">{item.confidence_explanation}</p>
            <p className="small">Status: {item.claim.status}</p>
            {item.matches.map((match, index) => (
              <p className="small" key={index}>
                Source {match.source_id || match.interview_id} • Score {match.match_score.toFixed(2)}
              </p>
            ))}
          </div>
        ))}
      </div>

      <div className="card">
        <h2>Export</h2>
        <button onClick={() => copy(markdown)}>Copy markdown</button>
        <button className="secondary" onClick={() => copy(jsonReport)}>
          Copy JSON
        </button>
        <textarea rows={6} value={markdown} readOnly />
      </div>
    </main>
  );
}
