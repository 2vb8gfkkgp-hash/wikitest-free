const feed = document.getElementById("feed");
const statusEl = document.getElementById("connection-status");

const formatTime = (value) => new Date(value).toLocaleTimeString();

const addEvent = (event) => {
  const item = document.createElement("li");
  item.innerHTML = `
    <strong>${event.query}</strong>
    <small>${event.label ? `Label: ${event.label} • ` : ""}${formatTime(event.createdAt)}</small>
    <small>Session: ${event.sessionId}</small>
  `;
  feed.prepend(item);
};

const connect = () => {
  const source = new EventSource("/api/events");

  source.addEventListener("open", () => {
    statusEl.textContent = "Connected";
    statusEl.style.color = "#10b981";
  });

  source.addEventListener("error", () => {
    statusEl.textContent = "Reconnecting…";
    statusEl.style.color = "#f59e0b";
  });

  source.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    addEvent(data);
  });
};

connect();
