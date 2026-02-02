const createButton = document.getElementById("create-session");
const output = document.getElementById("session-output");
const urlInput = document.getElementById("session-url");
const copyButton = document.getElementById("copy-link");

const createSession = async () => {
  createButton.disabled = true;
  const response = await fetch("/api/session", { method: "POST" });
  const data = await response.json();
  const fullUrl = `${window.location.origin}${data.url}`;

  urlInput.value = fullUrl;
  output.hidden = false;
  createButton.disabled = false;
};

createButton.addEventListener("click", createSession);

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(urlInput.value);
  copyButton.textContent = "Copied!";
  setTimeout(() => {
    copyButton.textContent = "Copy";
  }, 1500);
});
