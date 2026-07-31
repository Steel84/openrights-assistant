const state = { chunks: [], idf: {} };
const words = (text) => (text.toLowerCase().match(/[a-z0-9][a-z0-9'-]{1,}/g) || []);

function score(question, chunk) {
  const query = words(question);
  const counts = Object.create(null);
  words(chunk.text).forEach((word) => { counts[word] = (counts[word] || 0) + 1; });
  const length = words(chunk.text).length || 1;
  let value = 0;
  query.forEach((word) => { value += ((counts[word] || 0) / length) * (state.idf[word] || 1); });
  return value;
}

function showResults(question) {
  const results = state.chunks.map((chunk) => ({ ...chunk, score: score(question, chunk) }))
    .sort((a, b) => b.score - a.score).slice(0, 5);
  const container = document.querySelector("#results");
  container.innerHTML = `<div class="empty">${results.length ? `Showing ${results.length} source passages for “${escapeHtml(question)}”.` : "No matching passage found."}</div>`;
  results.forEach((result, index) => {
    const card = document.createElement("article");
    card.className = "result";
    card.innerHTML = `<div class="resulthead"><span>[${index + 1}] ${escapeHtml(result.source)}</span><span class="score">${result.score.toFixed(3)}</span></div><p>${escapeHtml(result.text)}</p><a href="${result.url}" target="_blank" rel="noreferrer">Open source ↗</a>`;
    container.appendChild(card);
  });
}

function escapeHtml(value) { return value.replace(/[&<>"']/g, (char) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", "\"":"&quot;", "'":"&#039;" }[char])); }

async function init() {
  try {
    const response = await fetch("./data/index.json");
    const payload = await response.json();
    state.chunks = payload.chunks || [];
    state.idf = payload.idf || {};
    document.querySelector("#chunkCount").textContent = state.chunks.length;
    document.querySelector("#statusText").textContent = "Ready · on this device";
  } catch (error) {
    document.querySelector("#statusText").textContent = "Archive unavailable";
    document.querySelector("#results").innerHTML = '<div class="empty">Run the export step before opening this app.</div>';
  }
}

document.querySelector("#searchForm").addEventListener("submit", (event) => {
  event.preventDefault();
  showResults(document.querySelector("#question").value.trim());
});
document.querySelectorAll("[data-question]").forEach((button) => button.addEventListener("click", () => {
  document.querySelector("#question").value = button.dataset.question;
  showResults(button.dataset.question);
}));
if ("serviceWorker" in navigator) navigator.serviceWorker.register("./service-worker.js");
init();
