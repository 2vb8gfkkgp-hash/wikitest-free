const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const labelInput = document.getElementById("label");
const resultsEl = document.getElementById("results");
const articleEl = document.getElementById("article");

const sessionKey = "wikitest-session";
let sessionId = localStorage.getItem(sessionKey);

if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem(sessionKey, sessionId);
}

const renderResults = (items) => {
  resultsEl.innerHTML = "";
  articleEl.innerHTML = "";

  if (!items.length) {
    resultsEl.classList.add("empty");
    resultsEl.textContent = "No results found.";
    return;
  }

  resultsEl.classList.remove("empty");
  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "result-item";
    card.innerHTML = `<strong>${item.title}</strong><p>${item.snippet}</p>`;

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Open summary";
    button.addEventListener("click", () => loadArticle(item.title));

    card.appendChild(button);
    resultsEl.appendChild(card);
  });
};

const loadArticle = async (title) => {
  articleEl.innerHTML = "Loading article…";
  const params = new URLSearchParams({
    action: "query",
    prop: "extracts",
    exintro: "1",
    explaintext: "1",
    titles: title,
    format: "json",
    origin: "*"
  });

  const response = await fetch(`https://en.wikipedia.org/w/api.php?${params}`);
  const data = await response.json();
  const page = Object.values(data.query.pages)[0];

  articleEl.innerHTML = `
    <h3>${page.title}</h3>
    <p>${page.extract || "No summary available."}</p>
  `;
};

const submitSearch = async (query, label) => {
  await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, sessionId, label })
  });
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  const label = labelInput.value.trim();

  if (!query) return;

  form.querySelector("button").disabled = true;

  await submitSearch(query, label || null);

  const params = new URLSearchParams({
    action: "query",
    list: "search",
    srsearch: query,
    srlimit: "5",
    format: "json",
    origin: "*"
  });

  const response = await fetch(`https://en.wikipedia.org/w/api.php?${params}`);
  const data = await response.json();

  const items = data.query.search.map((item) => ({
    title: item.title,
    snippet: item.snippet.replace(/<[^>]+>/g, "")
  }));

  renderResults(items);
  form.querySelector("button").disabled = false;
});
