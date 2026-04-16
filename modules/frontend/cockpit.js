/* =============================================================================
   CoreBuilderVX — Cockpit JavaScript
   Communicates with the local CBX API and drives the UI
   ============================================================================= */
"use strict";

// ---- Config (can be updated in Settings panel) ------------------------------
function _sanitiseHost(val) {
    // Allow only hostname chars, IPv4, or localhost — no port, no protocol
    return /^[a-zA-Z0-9.\-]{1,253}$/.test(val) ? val : "127.0.0.1";
}
function _sanitisePort(val) {
    const p = parseInt(val, 10);
    return (p >= 1 && p <= 65535) ? p : 8765;
}
let API_BASE = `http://${_sanitiseHost(localStorage.getItem("cbx-api-host") || "127.0.0.1")}:${_sanitisePort(localStorage.getItem("cbx-api-port") || "8765")}`;

// ---- Clock -------------------------------------------------------------------
(function tickClock() {
  const el = document.getElementById("clock");
  if (el) el.textContent = new Date().toLocaleTimeString();
  setTimeout(tickClock, 1000);
})();

// ---- Panel navigation -------------------------------------------------------
function showPanel(name) {
  document.querySelectorAll(".cbx-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".cbx-nav li").forEach(l => l.classList.remove("active"));
  const panel = document.getElementById(`panel-${name}`);
  const navEl  = document.querySelector(`[data-panel="${name}"]`);
  if (panel) panel.classList.add("active");
  if (navEl)  navEl.classList.add("active");

  // Lazy-load panel data
  if (name === "hardware") loadHardware();
  if (name === "logs")     loadLogs();
  if (name === "ai")       checkAiBackend();
  if (name === "dashboard") loadBuilds();
  if (name === "sitebuilder") { wbShowTab("list"); }
}

document.querySelectorAll(".cbx-nav li").forEach(li => {
  li.addEventListener("click", () => showPanel(li.dataset.panel));
});

// ---- Toast ------------------------------------------------------------------
function toast(msg, duration = 2500) {
  const el = document.getElementById("cbx-toast");
  el.textContent = msg;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), duration);
}

// ---- API fetch helper -------------------------------------------------------
async function apiFetch(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

// ---- API status check -------------------------------------------------------
async function checkApiStatus() {
  const el = document.getElementById("api-status");
  const data = await apiFetch("/api/v1/status");
  if (data && data.status === "ok") {
    el.textContent = `API ✓ v${data.version}`;
    el.className = "cbx-badge cbx-badge-green";
  } else {
    el.textContent = "API ✗";
    el.className = "cbx-badge cbx-badge-red";
  }
}

// ---- Hardware ---------------------------------------------------------------
async function loadHardware() {
  const tbody = document.getElementById("hw-tbody");
  const header = document.getElementById("hw-tier");
  const ramBadge = document.getElementById("hw-ram");
  const data = await apiFetch("/api/v1/hardware");

  if (data.error) {
    tbody.innerHTML = `<tr><td colspan="2" class="cbx-loading">${data.error}</td></tr>`;
    return;
  }

  header.textContent  = data.CBX_HW_TIER  || "–";
  ramBadge.textContent = (data.CBX_HW_RAM_MB ? data.CBX_HW_RAM_MB + "MB" : "–");

  const rows = Object.entries(data)
    .filter(([k]) => k.startsWith("CBX_HW_"))
    .map(([k, v]) => `<tr><td>${k.replace("CBX_HW_", "")}</td><td>${v}</td></tr>`)
    .join("");
  tbody.innerHTML = rows || `<tr><td colspan="2" class="cbx-loading">No hardware data</td></tr>`;
}

// ---- Builds -----------------------------------------------------------------
async function loadBuilds() {
  const tbody = document.getElementById("builds-tbody");
  const data  = await apiFetch("/api/v1/builds");
  if (data.error) {
    tbody.innerHTML = `<tr><td colspan="5" class="cbx-loading">${data.error}</td></tr>`;
    return;
  }
  if (!data.builds || data.builds.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="cbx-loading">No builds yet — use OS Builder</td></tr>`;
    return;
  }
  tbody.innerHTML = data.builds.slice(0, 10).map(b => `
    <tr>
      <td>${b.name  || "–"}</td>
      <td>${b.type  || "–"}</td>
      <td>${b.arch  || "–"}</td>
      <td>${b.built_at ? b.built_at.slice(0,16) : "–"}</td>
      <td style="color:${b.status==='complete'?'var(--green)':'var(--yellow)'}">${b.status || "–"}</td>
    </tr>
  `).join("");
}

// ---- Logs -------------------------------------------------------------------
async function loadLogs() {
  const el   = document.getElementById("log-output");
  const data = await apiFetch("/api/v1/logs");
  if (data.error) { el.textContent = data.error; return; }
  el.textContent = (data.log || []).join("\n") || "No logs yet.";
  el.scrollTop   = el.scrollHeight;
}

// ---- Run a command via API --------------------------------------------------
async function runCommand(cmd, outputId) {
  const outEl = outputId ? document.getElementById(outputId) : null;
  if (outEl) { outEl.style.display = "block"; outEl.textContent = `Running ${cmd}...`; }
  toast(`Running: ${cmd}`);

  const data = await apiFetch("/api/v1/run", {
    method: "POST",
    body: JSON.stringify({ command: cmd })
  });

  let output = "";
  if (data.error)  output = `Error: ${data.error}`;
  else             output = (data.stdout || "") + (data.stderr ? `\n[stderr] ${data.stderr}` : "");

  if (outEl) {
    outEl.textContent = output || "(no output)";
    outEl.scrollTop   = outEl.scrollHeight;
  }

  if (data.returncode === 0) toast(`✓ ${cmd} complete`);
  else toast(`✗ ${cmd} failed (code ${data.returncode})`, 4000);

  return data;
}

// ---- Builder form -----------------------------------------------------------
document.getElementById("builder-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const outEl = document.getElementById("builder-output");
  outEl.style.display = "block";
  outEl.textContent = "Starting build...";

  const env = {
    CBX_OS_TYPE:       document.getElementById("build-type").value,
    CBX_OS_ARCH:       document.getElementById("build-arch").value,
    CBX_BUILD_NAME:    document.getElementById("build-name").value || undefined,
    CBX_BUILD_MODULES: document.getElementById("build-modules").value,
  };

  const data = await apiFetch("/api/v1/run", {
    method: "POST",
    body: JSON.stringify({ command: "build", env })
  });

  outEl.textContent = (data.stdout || "") || (data.error || "Build triggered in shell");
  outEl.scrollTop   = outEl.scrollHeight;
  toast(data.returncode === 0 ? "✓ Build complete" : "✗ Build failed", 3000);
  loadBuilds();
});

// ---- AI backend check -------------------------------------------------------
async function checkAiBackend() {
  const statusEl = document.getElementById("ai-status");
  statusEl.textContent = "Note: AI Runner requires the shell interface.\n" +
    "Run: ./core.sh ai\n\n" +
    "Supported backends: ollama, llama.cpp, gpt4all, transformers\n" +
    "Install ollama for best Termux experience:\n  pkg install ollama  (or visit ollama.com)";
}

// Stub: AI chat via stub responses (no real model in browser)
function sendAiMessage() {
  const input  = document.getElementById("ai-input");
  const log    = document.getElementById("ai-chat-log");
  const msg    = input.value.trim();
  if (!msg) return;
  log.textContent += `\nYou: ${msg}\n`;
  input.value = "";
  setTimeout(() => {
    log.textContent += `AI:  [Use ./core.sh ai for real AI chat]\n`;
    log.scrollTop = log.scrollHeight;
  }, 300);
}

// ---- Settings ---------------------------------------------------------------
function saveSettings() {
  const host = _sanitiseHost(document.getElementById("s-api-host").value.trim());
  const port = _sanitisePort(document.getElementById("s-api-port").value.trim());
  localStorage.setItem("cbx-api-host", host);
  localStorage.setItem("cbx-api-port", port);
  API_BASE = `http://${host}:${port}`;
  toast("Settings saved — reconnecting...");
  checkApiStatus();
}

// ---- Website Builder --------------------------------------------------------

/** Switch between "New Site" and "My Sites" tabs. */
function wbShowTab(tab) {
  document.getElementById("wb-pane-new").style.display  = tab === "new"  ? "" : "none";
  document.getElementById("wb-pane-list").style.display = tab === "list" ? "" : "none";
  document.getElementById("wb-tab-new").className  =
    "cbx-btn" + (tab === "new"  ? " cbx-btn-primary" : "");
  document.getElementById("wb-tab-list").className =
    "cbx-btn" + (tab === "list" ? " cbx-btn-primary" : "");
  if (tab === "list") loadSites();
}

/** Load and render the sites table. */
async function loadSites() {
  const tbody = document.getElementById("wb-sites-tbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="6" class="cbx-loading">Loading…</td></tr>`;
  const data = await apiFetch("/api/v1/sites");
  if (data.error || !data.sites) {
    tbody.innerHTML = `<tr><td colspan="6" class="cbx-loading">${data.error || "No data"}</td></tr>`;
    return;
  }
  if (!data.sites.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="cbx-loading">
      No sites yet — use the "New Site" tab to create one.</td></tr>`;
    return;
  }
  tbody.innerHTML = data.sites.map(s => {
    const created = s.created_at ? s.created_at.slice(0, 10) : "–";
    const built   = s.last_build ? s.last_build.slice(0, 16) : "never";
    return `<tr>
      <td><strong>${_esc(s.name)}</strong></td>
      <td>${_esc(s.template || "–")}</td>
      <td>${_esc(s.mode || "–")}</td>
      <td>${created}</td>
      <td style="color:${s.last_build ? 'var(--green)' : 'var(--muted)'}">${built}</td>
      <td>
        <button class="cbx-btn" style="font-size:0.75rem;padding:2px 8px"
                onclick="wbBuildSite('${_esc(s.name)}')">⚙ Build</button>
        <button class="cbx-btn" style="font-size:0.75rem;padding:2px 8px;margin-left:4px"
                onclick="wbDeleteSite('${_esc(s.name)}')">🗑</button>
      </td>
    </tr>`;
  }).join("");
}

/** Build a site via the API and show progress. */
async function wbBuildSite(name) {
  const outEl = document.getElementById("wb-action-output");
  outEl.style.display = "block";
  outEl.textContent   = `Building '${name}'…`;
  toast(`Building ${name}…`);

  const data = await apiFetch(`/api/v1/sites/${encodeURIComponent(name)}/build`, {
    method: "POST",
  });

  if (data.error) {
    outEl.textContent = `✗ Error: ${data.error}`;
    toast(`✗ Build failed for ${name}`, 4000);
  } else {
    outEl.textContent =
      `✓ Build complete for '${name}'.\n` +
      `  Output: ${data.build_dir || "(unknown)"}\n\n` +
      `  To preview, run from terminal:\n` +
      `  cd "${data.build_dir || "…/_build"}"\n` +
      `  python3 -m http.server 8767 --bind 127.0.0.1\n` +
      `  Open: http://127.0.0.1:8767/index.html`;
    toast(`✓ ${name} built`);
    loadSites();
  }
}

/** Delete a site after confirmation. */
async function wbDeleteSite(name) {
  if (!confirm(`Delete site '${name}' and all its files? This cannot be undone.`)) return;
  const data = await apiFetch(`/api/v1/sites/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
  if (data.error) {
    toast(`✗ Delete failed: ${data.error}`, 4000);
  } else {
    toast(`✓ '${name}' deleted`);
    loadSites();
  }
}

/** HTML-escape a string for safe insertion into innerHTML. */
function _esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// Create-site form submission
document.getElementById("wb-create-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const outEl = document.getElementById("wb-create-output");
  outEl.style.display = "block";
  outEl.textContent   = "Creating site…";

  const data = await apiFetch("/api/v1/sites", {
    method: "POST",
    body: JSON.stringify({
      name:        document.getElementById("wb-name").value.trim(),
      template:    document.getElementById("wb-template").value,
      title:       document.getElementById("wb-title").value.trim(),
      description: document.getElementById("wb-desc").value.trim(),
      mode:        document.getElementById("wb-mode").value,
    }),
  });

  if (data.error) {
    outEl.textContent = `✗ Error: ${data.error}`;
    toast(`✗ ${data.error}`, 4000);
  } else {
    outEl.textContent =
      `✓ Site '${data.name}' created!\n\n` +
      `  Template    : ${data.template}\n` +
      `  Mode        : ${data.mode}\n` +
      `  Title       : ${data.title}\n\n` +
      `  Switch to "My Sites" and click Build to generate the static output.`;
    toast(`✓ '${data.name}' created`);
    document.getElementById("wb-create-form").reset();
  }
});

// ---- Init -------------------------------------------------------------------
(async function init() {
  // Restore settings
  document.getElementById("s-api-host").value = localStorage.getItem("cbx-api-host") || "127.0.0.1";
  document.getElementById("s-api-port").value = localStorage.getItem("cbx-api-port") || "8765";

  await checkApiStatus();
  await loadBuilds();
  await loadHardware();

  // Poll API status every 15s
  setInterval(checkApiStatus, 15000);
})();
