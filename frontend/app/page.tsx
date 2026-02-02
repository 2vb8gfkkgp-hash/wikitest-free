"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet, apiSend } from "../lib/api";

interface Project {
  id: number;
  title: string;
  topic: string;
  audience?: string;
  deadline?: string;
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [form, setForm] = useState({ title: "", topic: "", audience: "", deadline: "" });

  const loadProjects = async () => {
    const data = await apiGet<Project[]>("/projects");
    setProjects(data);
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const submit = async () => {
    await apiSend<Project>("/projects", "POST", {
      title: form.title,
      topic: form.topic,
      audience: form.audience || null,
      deadline: form.deadline || null,
    });
    setForm({ title: "", topic: "", audience: "", deadline: "" });
    loadProjects();
  };

  return (
    <main>
      <header>
        <div>
          <h1>NewsroomKit</h1>
          <p className="small">
            A transparent, ethical newsroom assistant for students.
          </p>
        </div>
      </header>

      <div className="card">
        <h2>Create a project</h2>
        <div className="grid grid-2">
          <div>
            <label>Title</label>
            <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <label>Topic</label>
            <input value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} />
          </div>
          <div>
            <label>Audience (optional)</label>
            <input value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} />
          </div>
          <div>
            <label>Deadline (optional)</label>
            <input type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
          </div>
        </div>
        <button onClick={submit}>Create project</button>
      </div>

      <div className="card">
        <h2>Projects</h2>
        <div className="grid">
          {projects.map((project) => (
            <div key={project.id} className="card">
              <h3>{project.title}</h3>
              <p className="small">{project.topic}</p>
              <Link href={`/projects/${project.id}`}>Open project →</Link>
            </div>
          ))}
          {projects.length === 0 && <p className="small">No projects yet.</p>}
        </div>
      </div>
    </main>
  );
}
