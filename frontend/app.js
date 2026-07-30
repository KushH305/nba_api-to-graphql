const GRAPHQL_URL = "http://127.0.0.1:8000/graphql";
const REST_BASE = "http://127.0.0.1:8001";

const SCENARIOS = {
  1: {
    graphql: '{ player(name: "Bam Adebayo") { firstName lastName position jerseyNumber } }',
    rest: [`${REST_BASE}/players/Bam%20Adebayo`],
  },
  2: {
    graphql: '{ team(id: 16) { fullName roster { firstName lastName } recentGames(limit: 5) { date homeScore visitorScore } } }',
    rest: [
      `${REST_BASE}/teams/16`,
      `${REST_BASE}/teams/16/roster`,
      `${REST_BASE}/teams/16/games?limit=5`,
    ],
  },
  3: {
    graphql: '{ teams(ids: [16, 2, 14, 20, 6]) { fullName recentGames(limit: 5) { date homeScore visitorScore } } }',
    rest: [16, 2, 14, 20, 6].map(id => `${REST_BASE}/teams/${id}/games?limit=5`),
  },
};

const statusNote = document.getElementById("status-note");

async function runScenario(num, btnEl) {
  document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
  btnEl.classList.add("active");

  const buttons = document.querySelectorAll(".scenario-btn");
  buttons.forEach(b => (b.disabled = true));
  statusNote.textContent = "Running…";
  document.getElementById("progress-track").classList.add("active");

  const scenario = SCENARIOS[num];
  await Promise.all([
    runGraphQL(scenario.graphql),
    runRest(scenario.rest),
  ]);

  buttons.forEach(b => (b.disabled = false));
  statusNote.textContent = "Both servers must be running locally (ports 8000 and 8001).";
  document.getElementById("progress-track").classList.remove("active");
}

async function runGraphQL(query) {
  const outputEl = document.getElementById("graphql-output");
  outputEl.classList.remove("is-error");

  try {
    const start = performance.now();
    const resp = await fetch(GRAPHQL_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const text = await resp.text();
    const duration = performance.now() - start;

    if (!resp.ok) throw new Error(`Server responded ${resp.status}`);

    const parsed = JSON.parse(text);
    lastResponse.graphql = parsed;
    outputEl.innerHTML = syntaxHighlight(JSON.stringify(parsed, null, 2));
    setStats("graphql", duration, new Blob([text]).size, 1);
  } catch (err) {
    outputEl.classList.add("is-error");
    outputEl.textContent = `Request failed: ${err.message}\n\nIs the GraphQL server running on port 8000?`;
    setStats("graphql", "—", "—", "—");
  }
}

async function runRest(urls) {
  const outputEl = document.getElementById("rest-output");
  outputEl.classList.remove("is-error");

  try {
    const start = performance.now();
    let totalBytes = 0;
    const results = [];

    for (const url of urls) {
      const resp = await fetch(url);
      const text = await resp.text();
      if (!resp.ok) throw new Error(`Server responded ${resp.status} for ${url}`);
      totalBytes += new Blob([text]).size;
      results.push(JSON.parse(text));
    }

    const duration = performance.now() - start;
    lastResponse.rest = results;
    outputEl.innerHTML = syntaxHighlight(JSON.stringify(results, null, 2));
    setStats("rest", duration, totalBytes, urls.length);
  } catch (err) {
    outputEl.classList.add("is-error");
    outputEl.textContent = `Request failed: ${err.message}\n\nIs the REST server running on port 8001?`;
    setStats("rest", "—", "—", "—");
  }
}

function setStats(prefix, time, size, calls) {
  document.getElementById(`${prefix}-time`).textContent = typeof time === "number" ? time.toFixed(1) : time;
  document.getElementById(`${prefix}-size`).textContent = size;
  document.getElementById(`${prefix}-calls`).textContent = calls;
}

// Store the last successful raw responses so the modal can show them
const lastResponse = { rest: null, graphql: null };

// --- JSON syntax highlighter ---
function syntaxHighlight(jsonString) {
  const escaped = jsonString
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return escaped.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = "json-number";
      if (/^"/.test(match)) {
        cls = /:$/.test(match) ? "json-key" : "json-string";
      } else if (/true|false/.test(match)) {
        cls = "json-boolean";
      } else if (/null/.test(match)) {
        cls = "json-null";
      }
      return `<span class="${cls}">${match}</span>`;
    }
  );
}

// --- Modal controls ---
function openModal(source) {
  const data = lastResponse[source];
  if (!data) return;

  document.getElementById("modal-tag").textContent = source === "graphql" ? "GRAPHQL" : "REST";
  document.getElementById("modal-title").textContent = source === "graphql" ? "GraphQL response" : "REST response";
  document.getElementById("modal-code").innerHTML = syntaxHighlight(JSON.stringify(data, null, 2));
  document.getElementById("modal-overlay").classList.add("open");
  document.getElementById("copy-btn").dataset.source = source;
}

function closeModal() {
  document.getElementById("modal-overlay").classList.remove("open");
}

function closeModalOnBackdrop(event) {
  if (event.target.id === "modal-overlay") closeModal();
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

function copyModalContent() {
  const source = document.getElementById("copy-btn").dataset.source;
  const text = JSON.stringify(lastResponse[source], null, 2);
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById("copy-btn");
    const original = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => (btn.textContent = original), 1200);
  });
}