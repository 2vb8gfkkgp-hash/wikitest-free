"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "../../../../../lib/api";

interface Claim {
  id: number;
  text: string;
  category: string;
  claim_type?: string;
  status: string;
  confidence: number;
}

interface Match {
  id: number;
  source_id?: number;
  interview_id?: number;
  match_score: number;
  overlap?: string;
  needs_review: boolean;
}

interface EvidenceItem {
  claim: Claim;
  matches: Match[];
  confidence_explanation: string;
}

interface Checklist {
  right_of_reply: boolean;
  separate_fact_opinion: boolean;
  avoid_sensational: boolean;
  quote_integrity: boolean;
}

export default function ClaimDetail({ params }: { params: { id: string; claimId: string } }) {
  const [item, setItem] = useState<EvidenceItem | null>(null);
  const [checklist, setChecklist] = useState<Checklist | null>(null);
  const projectId = params.id;
  const claimId = parseInt(params.claimId, 10);

  useEffect(() => {
    const load = async () => {
      const report = await apiGet<{ items: EvidenceItem[] }>(`/projects/${projectId}/report`);
      const checklistData = await apiGet<Checklist>(`/projects/${projectId}/checklist`);
      setChecklist(checklistData);
      const found = report.items.find((entry) => entry.claim.id === claimId);
      setItem(found || null);
    };
    load();
  }, [projectId, claimId]);

  const checklistIncomplete =
    checklist && (!checklist.right_of_reply || !checklist.separate_fact_opinion || !checklist.avoid_sensational || !checklist.quote_integrity);

  return (
    <main>
      <header>
        <h1>Claim detail</h1>
        <Link href={`/projects/${projectId}`}>Back to project</Link>
      </header>

      {item ? (
        <div className="card">
          <h2>{item.claim.text}</h2>
          <p className="small">
            {item.claim.category} • {item.claim.claim_type} • {item.claim.status} (confidence {item.claim.confidence.toFixed(2)})
          </p>
          <p className="small">{item.confidence_explanation}</p>

          {item.claim.claim_type === "allegation" && checklistIncomplete && (
            <p className="danger">
              Allegation detected: complete the ethical checklist or flag this claim prominently.
            </p>
          )}

          <h3>Matches</h3>
          {item.matches.map((match) => (
            <div className="card" key={match.id}>
              <p className="small">Score: {match.match_score.toFixed(2)}</p>
              {match.needs_review && <p className="warning">Needs review</p>}
              {match.overlap && <p className="small">Overlap: {match.overlap}</p>}
            </div>
          ))}
          {item.matches.length === 0 && <p className="small">No sources found.</p>}
        </div>
      ) : (
        <p className="small">Loading claim...</p>
      )}
    </main>
  );
}
