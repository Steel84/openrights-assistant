const state = { chunks: [], idf: {}, ready: false };
const TOKEN = /[a-z0-9][a-z0-9'-]{1,}/g;
const ANSWER_FLOOR = 0.35;
const GENERIC_WORDS = new Set("what when where which while about have does can the are from with without and get how been being same other their there they this that these those your not all any some more most much many into over under than then such only own just also need want should would could will shall".split(" "));

function subjectWords(question) {
  return words(question).filter((word) => word.length >= 4 && !GENERIC_WORDS.has(word));
}

const EVIDENCE_TERMS = 2;

function onSubject(question, text, idf, terms = 1) {
  const subjects = subjectWords(question);
  if (!subjects.length) return true;
  const known = subjects.filter((word) => idf[word] !== undefined);
  if (terms === 1 && known.length !== subjects.length) return false;
  if (!known.length) return true;
  const ranked = [...known].sort((a, b) => idf[b] - idf[a]).slice(0, terms);
  const present = new Set(words(text));
  return ranked.some((word) => present.has(word));
}

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

function renderAnswer(body) {
  return body
    .split(/\n\s*\n/)
    .map((para) => para.trim())
    .filter(Boolean)
    .map((para) => `<p>${escapeHtml(para).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")}</p>`)
    .join("");
}

function highlight(text, question) {
  const terms = [...new Set(words(question))].filter((term) => term.length > 3);
  const escaped = escapeHtml(text);
  if (!terms.length) return escaped;
  const pattern = new RegExp(`\\b(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "gi");
  return escaped.replace(pattern, "<mark>$1</mark>");
}

function excerpt(text, question, size) {
  const terms = words(question).filter((term) => term.length > 3);
  const tokens = text.split(/\s+/);
  if (tokens.length <= size) return text;
  let start = 0;
  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i].toLowerCase();
    if (terms.some((term) => token.includes(term))) {
      start = Math.max(0, i - 12);
      break;
    }
  }
  const slice = tokens.slice(start, start + size).join(" ");
  return `${start > 0 ? "\u2026 " : ""}${slice}${start + size < tokens.length ? " \u2026" : ""}`;
}

function splitHeading(text) {
  const [heading, ...rest] = text.split(/\n\s*\n/);
  return { heading: heading.trim(), body: rest.join("\n\n").trim() };
}

function answerCard(hit, question) {
  const { chunk } = hit;
  const parsed = splitHeading(chunk.text);
  const heading = chunk.heading || parsed.heading;
  const body = chunk.body || parsed.body;
  const card = document.createElement("article");
  card.className = "answer";
  card.innerHTML = `
    <p class="answerlabel">Answer</p>
    <h3>${escapeHtml(heading)}</h3>
    ${renderAnswer(body)}
    <p class="answermeta">${escapeHtml(chunk.statute || chunk.source)} \u00b7 <a href="${escapeHtml(chunk.url)}" target="_blank" rel="noreferrer">read the law</a></p>`;
  return card;
}

function passageCard(hit, index, question) {
  const { chunk } = hit;
  const card = document.createElement("article");
  card.className = "result";
  card.innerHTML = `
    <div class="resulthead"><span>[${index}] ${escapeHtml(chunk.source)}</span></div>
    <p>${highlight(excerpt(chunk.text, question, 70), question)}</p>
    <a href="${escapeHtml(chunk.url)}" target="_blank" rel="noreferrer">Open source \u2197</a>`;
  return card;
}

// --- AI Summary (Gemini + Mistral fallback) ---
const PROVIDERS = [
  {
    name: 'gemini',
    url: 'https://gemini.fortravels.xyz/?key=' + (window.OPENRIGHTS_CONFIG?.geminiKey || '') + '&model=gemini-flash-latest',
    buildBody: (prompt) => JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.2, maxOutputTokens: 4096 }
    }),
    parseResponse: (data) => {
      const parts = data?.candidates?.[0]?.content?.parts;
      if (!parts || !parts.length) return null;
      const textPart = parts.find(p => p.text && !p.thought) || parts[parts.length - 1];
      return textPart?.text?.trim() || null;
    },
    headers: { 'Content-Type': 'application/json' }
  },
  {
    name: 'mistral',
    url: 'https://api.mistral.ai/v1/chat/completions',
    buildBody: (prompt) => JSON.stringify({
      model: 'mistral-small-latest',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 1024,
      temperature: 0.2
    }),
    parseResponse: (data) => data?.choices?.[0]?.message?.content?.trim() || null,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + (window.OPENRIGHTS_CONFIG?.mistralKey || '')
    }
  }
];
let _geminiRequestId = 0;
let _geminiAbort = null;

async function geminiSummary(question, passages, requestId) {
  const sources = passages.map((p, i) =>
    `[${i+1}] ${p.chunk.source}\n${(p.chunk.body || p.chunk.text).slice(0, 600)}\nURL: ${p.chunk.url}`
  ).join('\n\n');

  const prompt = `You are a helpful legal information assistant. Synthesize the passages below into a clear, detailed answer to the question. Include specific rules, numbers, deadlines, thresholds, and exceptions when present. Do not use citation numbers like [1] or [2]. Write 100-200 words. Plain English. This is information, not legal advice.\n\nQuestion: ${question}\n\nPassages:\n${sources}\n\nAnswer:`;

  if (_geminiAbort) _geminiAbort.abort();
  _geminiAbort = new AbortController();

  // Try each provider in order (Gemini first, Mistral as fallback)
  for (const provider of PROVIDERS) {
    if (requestId !== _geminiRequestId) return null;
    try {
      const resp = await fetch(provider.url, {
        signal: _geminiAbort.signal,
        method: 'POST',
        headers: provider.headers,
        body: provider.buildBody(prompt)
      });
      // If rate-limited or server error, try next provider
      if (resp.status === 429 || resp.status === 503) continue;
      if (!resp.ok) continue;
      const data = await resp.json();
      const text = provider.parseResponse(data);
      if (text) return text;
      // Empty response, try next
      continue;
    } catch (e) {
      if (e.name === 'AbortError') return null;
      // Network error, try next provider
      continue;
    }
  }
  return null;
}
// --- End AI Summary ---

function showResults(question) {
  const container = document.querySelector("#results");
  if (!state.ready) return;
  container.innerHTML = "";

  // Increment request ID to invalidate any in-flight Gemini request
  _geminiRequestId++;
  const myRequestId = _geminiRequestId;

  if (!question) {
    container.innerHTML = '<div class="empty">Type a question to search the local archive.</div>';
    return;
  }

  const hits = search(question, 40).filter((hit) => hit.score > 0);
  if (!hits.length) {
    container.innerHTML = '<div class="empty">Nothing in this archive matches that. Try different words.</div>';
    return;
  }

  const answer = hits.find(
    (hit) => hit.chunk.kind === "plain"
      && hit.score >= ANSWER_FLOOR
      && onSubject(question, hit.chunk.text, state.idf)
  );
  const passages = hits
    .filter((hit) => hit.chunk.kind !== "plain" && onSubject(question, hit.chunk.text, state.idf, EVIDENCE_TERMS))
    .slice(0, 4);

  if (answer) {
    container.appendChild(answerCard(answer, question));
  } else if (passages.length) {
    const notice = document.createElement("div");
    notice.className = "empty";
    notice.textContent = "No plain-language answer covers this yet. Here is the closest text in the law.";
    container.appendChild(notice);
  } else {
    container.innerHTML = '<div class="empty">This archive does not cover that topic yet. It covers pay and overtime, losing a job, family and medical leave, workplace safety, debt collection, credit reports, and workplace discrimination.</div>';
    return;
  }

  if (passages.length) {
    const details = document.createElement("details");
    details.className = "sources";
    if (!answer) details.open = true;
    const summary = document.createElement("summary");
    summary.textContent = `${passages.length} supporting passage${passages.length === 1 ? "" : "s"} from the law`;
    details.appendChild(summary);
    passages.forEach((hit, index) => details.appendChild(passageCard(hit, index + 1, question)));
    container.appendChild(details);
  }

  // AI Summary (if toggle is on)
  const aiToggle = document.getElementById('aiToggle');
  if (!aiToggle || !aiToggle.checked) return;
  const aiPassages = hits.filter(h => h.chunk.kind !== 'plain').slice(0, 5);
  if (!aiPassages.length) return;

  // Insert loading placeholder
  const aiDetails = document.createElement('details');
  aiDetails.className = 'ai-card';
  aiDetails.open = true;
  aiDetails.innerHTML = '<summary class="ai-label">AI Summary</summary><p class="ai-loading">Generating...</p>';
  container.appendChild(aiDetails);

  // Hard timeout: if no response in 15s, remove loader silently
  const hardTimeout = setTimeout(() => {
    if (myRequestId === _geminiRequestId && aiDetails.parentNode) {
      aiDetails.remove();
    }
  }, 15000);

  geminiSummary(question, aiPassages, myRequestId).then(text => {
    clearTimeout(hardTimeout);
    // Only render if this is still the active request
    if (myRequestId !== _geminiRequestId) return;
    if (!aiDetails.parentNode) return;

    const loader = aiDetails.querySelector('.ai-loading');
    if (text) {
      if (loader) loader.remove();
      const body = document.createElement('div');
      body.className = 'ai-body';
      body.innerHTML = renderAnswer(text);
      aiDetails.appendChild(body);
      const meta = document.createElement('p');
      meta.className = 'ai-meta';
      meta.textContent = 'AI-generated answer. May be inaccurate, always verify with the cited sources.';
      aiDetails.appendChild(meta);
    } else {
      // Show brief error instead of silent removal
      if (loader) loader.textContent = 'AI temporarily unavailable. Try again later.';
    }
  }).catch(() => {
    clearTimeout(hardTimeout);
    if (!aiDetails.parentNode) return;
    const loader = aiDetails.querySelector('.ai-loading');
    if (loader) loader.textContent = 'AI temporarily unavailable. Try again later.';
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
  statusText.textContent = "Ready \u00b7 on this device";
  document.querySelector("#results").innerHTML = '<div class="empty">Ask a question or pick an example below the search box.</div>';
}

const questionField = document.querySelector("#question");

const MAX_LINES = 4;
function fitToContent() {
  questionField.style.height = "auto";
  const line = parseFloat(getComputedStyle(questionField).lineHeight) || 24;
  const padding = questionField.offsetHeight - questionField.clientHeight;
  const ceiling = line * MAX_LINES + padding;
  questionField.style.height = `${Math.min(questionField.scrollHeight, ceiling)}px`;
  questionField.style.overflowY = questionField.scrollHeight > ceiling ? "auto" : "hidden";
}
questionField.addEventListener("input", fitToContent);

// Clear button
const clearBtn = document.querySelector("#clearBtn");
function updateClearBtn() {
  if (clearBtn) clearBtn.style.display = questionField.value.trim() ? "flex" : "none";
}
if (clearBtn) {
  clearBtn.addEventListener("click", () => {
    questionField.value = "";
    fitToContent();
    updateClearBtn();
    questionField.focus();
  });
}
questionField.addEventListener("input", updateClearBtn);

questionField.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    document.querySelector("#searchForm").requestSubmit();
  }
});

document.querySelector("#searchForm").addEventListener("submit", (event) => {
  event.preventDefault();
  showResults(questionField.value.trim());
});

document.querySelectorAll("[data-question]").forEach((button) => button.addEventListener("click", () => {
  questionField.value = button.dataset.question;
  fitToContent();
  updateClearBtn();
  showResults(button.dataset.question);
}));

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
  const hadController = Boolean(navigator.serviceWorker.controller);
  let reloading = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadController || reloading) return;
    reloading = true;
    location.reload();
  });
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
