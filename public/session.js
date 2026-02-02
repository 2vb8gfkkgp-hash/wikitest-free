const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const resultsEl = document.getElementById("results");
const articleEl = document.getElementById("article");

const sessionId = window.location.pathname.split("/").pop();

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
    card.className = "wiki-result-item";
    card.innerHTML = `
      <h3>${item.title}</h3>
      <p>${item.snippet}</p>
      <button type="button">Open summary</button>
    `;

    card.querySelector("button").addEventListener("click", () => loadArticle(item.title));
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
    <h2>${page.title}</h2>
    <p>${page.extract || "No summary available."}</p>
  `;
};

const submitSearch = async (query) => {
  await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, sessionId })
  });
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();

  if (!query) return;

  form.querySelector("button").disabled = true;
  await submitSearch(query);

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
