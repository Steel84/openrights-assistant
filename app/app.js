const state = { chunks: [], idf: {}, ready: false };
const TOKEN = /[a-z0-9][a-z0-9'-]{1,}/g;
const ANSWER_FLOOR = 0.35;
// Cosine similarity rewards sentence shape. "Can my landlord raise the rent?"
// scored 0.63 against "Can my employer change my schedule?" on "can my" alone,
// while landlord and rent appeared nowhere in the answer. A confident answer to
// a different question is the worst failure this tool can have, so the subject
// of the question has to actually appear in the answer.
const GENERIC_WORDS = new Set("what when where which while about have does can the are from with without and get how been being same other their there they this that these those your not all any some more most much many into over under than then such only own just also need want should would could will shall".split(" "));

function subjectWords(question) {
  return words(question).filter((word) => word.length >= 4 && !GENERIC_WORDS.has(word));
}

// Two callers, two standards, because the cost of being wrong differs. An
// answer must clear the strict test, and refuses outright when a subject word
// is missing from the corpus: a word the archive has never seen is the
// clearest signal it does not cover the topic, which is what makes this
// decline on rent and eviction instead of answering with an employment rule.
// Citations use the looser test and ignore unknown words, because one rare
// word is often a figure of speech rather than the topic: "getting a mortgage"
// contains *getting*, absent from every statute, and demanding it hid all of
// the Truth in Lending Act.
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

// The plain-language answers are written by this project, so a tiny, closed
// subset of Markdown is safe: paragraph breaks and **bold**. Everything is
// escaped first, so nothing in the archive can inject markup.
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

// Statute text runs for hundreds of words. Show the window around the first
// matching term instead of the arbitrary start of the chunk.
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
  // chunk.text is the search representation: the question repeated for weight,
  // plus alias phrasings. chunk.body is what a person should actually read.
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
    <div class="resulthead"><span>[${index}] ${escapeHtml(chunk.source)}</span><span class="score">${hit.score.toFixed(3)}</span></div>
    <p>${highlight(excerpt(chunk.text, question, 70), question)}</p>
    <a href="${escapeHtml(chunk.url)}" target="_blank" rel="noreferrer">Open source \u2197</a>`;
  return card;
}

function showResults(question) {
  const container = document.querySelector("#results");
  if (!state.ready) return;
  container.innerHTML = "";
  if (!question) {
    container.innerHTML = '<div class="empty">Type a question to search the local archive.</div>';
    return;
  }

  const hits = search(question, 40).filter((hit) => hit.score > 0);
  if (!hits.length) {
    container.innerHTML = '<div class="empty">Nothing in this archive matches that. Try different words.</div>';
    return;
  }

  // A weak plain-language match is worse than none: it reads as an
  // authoritative answer to a question it does not cover. Below the floor,
  // fall back to showing the law and saying so.
  const answer = hits.find(
    (hit) => hit.chunk.kind === "plain"
      && hit.score >= ANSWER_FLOOR
      && onSubject(question, hit.chunk.text, state.idf)
  );
  // Evidence is the law itself. Another plain-language answer is not evidence,
  // and an off-subject passage is noise dressed as a citation: a question about
  // a mortgage was being "supported" by the child labor rules.
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

  if (!passages.length) return;

  const details = document.createElement("details");
  details.className = "sources";
  if (!answer) details.open = true;
  const summary = document.createElement("summary");
  summary.textContent = `${passages.length} supporting passage${passages.length === 1 ? "" : "s"} from the law`;
  details.appendChild(summary);
  passages.forEach((hit, index) => details.appendChild(passageCard(hit, index + 1, question)));
  container.appendChild(details);
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

  // Cache-first means a returning visitor renders the previous release: the
  // new worker installs while the old one is still answering. Reload once when
  // control changes, so the new archive is what they read.
  //
  // Only when a worker was already in charge. On a first visit control passes
  // from nothing to the new worker, and the page is current already; reloading
  // there would be a visible flash for no reason.
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
