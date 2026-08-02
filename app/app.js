const state = { chunks: [], idf: {}, ready: false };
const TOKEN = /[a-z0-9][a-z0-9'-]{1,}/g;

const words = (text) => text.toLowerCase().match(TOKEN) || [];

function vector(text, idf) {
  const counts = Object.create(null);
  const tokens = words(text);
  tokens.forEach((word) => { counts[word] = (counts[word] || 0) + 1; });
  const length = tokens.length || 1;
  const result = Object.create(null);
  for (const word in counts) {
    if (idf[word] !== undefined) result[word] = (counts[word] / length) * idf[word];
  }
  return result;
}

function norm(vec) {
  let total = 0;
  for (const word in vec) total += vec[word] * vec[word];
  return Math.sqrt(total) || 1;
}

// Same cosine ranking as the Python CLI, so phone results match `openrights ask`.
function search(question, topK) {
  const query = vector(question, state.idf);
  const queryNorm = norm(query);
  return state.chunks
    .map((chunk) => {
      let dot = 0;
      for (const word in query) {
        const value = chunk.vector[word];
        if (value !== undefined) dot += query[word] * value;
      }
      return { chunk, score: dot / (queryNorm * chunk.norm) };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
}

function showResults(question) {
  const container = document.querySelector("#results");
  if (!state.ready) return;
  if (!question) {
    container.innerHTML = '<div class="empty">Type a question to search the local archive.</div>';
    return;
  }
  const hits = search(question, 5).filter((hit) => hit.score > 0);
  container.innerHTML = `<div class="empty">${hits.length ? `Showing ${hits.length} source passages for “${escapeHtml(question)}”.` : "No matching passage in this archive. Try different words."}</div>`;
  hits.forEach((hit, index) => {
    const card = document.createElement("article");
    card.className = "result";
    card.innerHTML = `<div class="resulthead"><span>[${index + 1}] ${escapeHtml(hit.chunk.source)}</span><span class="score">${hit.score.toFixed(3)}</span></div><p>${escapeHtml(hit.chunk.text)}</p><a href="${escapeHtml(hit.chunk.url)}" target="_blank" rel="noreferrer">Open source ↗</a>`;
    container.appendChild(card);
  });
}

function init() {
  const payload = window.OPENRIGHTS_INDEX;
  const statusText = document.querySelector("#statusText");
  if (!payload || !payload.chunks || !payload.chunks.length) {
    statusText.textContent = "Archive missing";
    document.querySelector("#results").innerHTML = '<div class="empty">The local archive did not load. Run <code>python -m openrights ingest &amp;&amp; python -m openrights export-web</code>, then reopen this page.</div>';
    return;
  }
  state.idf = payload.idf || {};
  state.chunks = payload.chunks.map((chunk) => {
    const vec = vector(chunk.text, state.idf);
    return { ...chunk, vector: vec, norm: norm(vec) };
  });
  state.ready = true;
  document.querySelector("#chunkCount").textContent = state.chunks.length;
  statusText.textContent = "Ready · on this device";
  document.querySelector("#results").innerHTML = '<div class="empty">Ask a question or pick an example below the search box.</div>';
}

document.querySelector("#searchForm").addEventListener("submit", (event) => {
  event.preventDefault();
  showResults(document.querySelector("#question").value.trim());
});

document.querySelectorAll("[data-question]").forEach((button) => button.addEventListener("click", () => {
  document.querySelector("#question").value = button.dataset.question;
  showResults(button.dataset.question);
}));

// Offline caching needs a service worker, and browsers only allow one in a
// secure context: https, or localhost. Plain http on a bare IP is refused, so
// registering there silently does nothing and the app looks broken in airplane
// mode. Say so instead of pretending. The APK runs from file:// and needs no
// worker, because its assets are already on the device.
function reportOfflineReadiness() {
  const status = document.querySelector("#statusText");
  if (!status || !state.ready) return;
  if (location.protocol === "file:") {
    status.textContent = "Ready \u00b7 on this device";
    return;
  }
  if (!("serviceWorker" in navigator) || !window.isSecureContext) {
    status.textContent = "Ready \u00b7 online only (needs https to save offline)";
    return;
  }
  const saved = () => { status.textContent = "Ready \u00b7 saved for offline"; };
  navigator.serviceWorker
    .register("./service-worker.js")
    .then((registration) => {
      if (navigator.serviceWorker.controller) return saved();
      const worker = registration.installing || registration.waiting;
      if (!worker) return saved();
      status.textContent = "Ready \u00b7 saving for offline\u2026";
      worker.addEventListener("statechange", () => {
        if (worker.state === "activated" || worker.state === "redundant") saved();
      });
    })
    .catch(() => { status.textContent = "Ready \u00b7 online only"; });
}

init();
reportOfflineReadiness();
