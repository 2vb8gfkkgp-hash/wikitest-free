import express from "express";
import { randomUUID } from "crypto";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const port = process.env.PORT || 3000;
const ntfyTopic = process.env.NTFY_TOPIC || "";
const __dirname = path.dirname(fileURLToPath(import.meta.url));

app.use(express.json({ limit: "32kb" }));
app.use(express.static("public"));

const events = [];
const subscribers = new Set();
const sessions = new Map();

const pushEvent = (event) => {
  events.push(event);
  if (events.length > 200) {
    events.shift();
  }
  const payload = `data: ${JSON.stringify(event)}\n\n`;
  for (const res of subscribers) {
    res.write(payload);
  }
};

const sendNotification = async (event) => {
  if (!ntfyTopic) return;
  const title = "Wikitest search";
  const body = `${event.query} — ${event.sessionId}`;
  try {
    await fetch(`https://ntfy.sh/${encodeURIComponent(ntfyTopic)}`, {
      method: "POST",
      headers: {
        Title: title,
        Priority: "4",
        Tags: "mag,eyes"
      },
      body
    });
  } catch (error) {
    console.error("Notification failed", error);
  }
};

app.get("/api/health", (_req, res) => {
  res.json({
    ok: true,
    notificationsEnabled: Boolean(ntfyTopic),
    activeSessions: sessions.size
  });
});

app.post("/api/session", (_req, res) => {
  const sessionId = randomUUID();
  const createdAt = new Date().toISOString();
  sessions.set(sessionId, { createdAt });
  res.json({
    sessionId,
    url: `/session/${sessionId}`
  });
});

app.get("/session/:sessionId", (req, res) => {
  const { sessionId } = req.params;
  if (!sessions.has(sessionId)) {
    res.status(404).send("Session not found.");
    return;
  }
  res.sendFile(path.join(__dirname, "public", "session.html"));
});

app.get("/api/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders();

  for (const event of events) {
    res.write(`data: ${JSON.stringify(event)}\n\n`);
  }

  subscribers.add(res);
  req.on("close", () => {
    subscribers.delete(res);
  });
});

app.post("/api/search", async (req, res) => {
  const { query, sessionId, label } = req.body || {};
  if (!query || !sessionId) {
    res.status(400).json({ error: "query and sessionId required" });
    return;
  }
  if (!sessions.has(sessionId)) {
    res.status(404).json({ error: "session not found" });
    return;
  }

  const event = {
    id: randomUUID(),
    query: String(query).slice(0, 200),
    sessionId: String(sessionId).slice(0, 80),
    label: label ? String(label).slice(0, 80) : null,
    createdAt: new Date().toISOString()
  };

  pushEvent(event);
  await sendNotification(event);

  res.json({ ok: true });
});

app.listen(port, () => {
  console.log(`Wikitest running at http://localhost:${port}`);
});
