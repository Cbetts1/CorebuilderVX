/**
 * CoreBuilderVX — Node.js API Engine (Express)
 * Lightweight REST API — alternative to the Python backend
 */

"use strict";

const http    = require("http");
const fs      = require("fs");
const path    = require("path");
const { execFile, spawn } = require("child_process");

const CBX_ROOT  = process.env.CBX_ROOT  || path.resolve(__dirname, "../..");
const API_HOST  = process.env.CBX_API_HOST  || "127.0.0.1";
const API_PORT  = parseInt(process.env.CBX_API_PORT || "8765", 10);
const LOG_FILE  = path.join(CBX_ROOT, "builds", "build.log");

// ---- Simple router ----------------------------------------------------------
const routes = Object.create(null);
function route(method, path, handler) {
    routes[`${method.toUpperCase()} ${path}`] = handler;
}

// ---- Helper: JSON response -------------------------------------------------
function json(res, statusCode, data) {
    const body = JSON.stringify(data, null, 2);
    res.writeHead(statusCode, {
        "Content-Type":  "application/json",
        "Content-Length": Buffer.byteLength(body),
        "Access-Control-Allow-Origin":  "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    });
    res.end(body);
}

// ---- Load hardware profile -------------------------------------------------
function loadHardware() {
    const confPath = path.join(CBX_ROOT, "config", "hardware.conf");
    const hw = {};
    if (fs.existsSync(confPath)) {
        const lines = fs.readFileSync(confPath, "utf8").split("\n");
        for (const line of lines) {
            const m = line.match(/^(CBX_HW_\w+)="?([^"]*)"?/);
            if (m) hw[m[1]] = m[2];
        }
    }
    return hw;
}

// ---- Routes -----------------------------------------------------------------
route("GET", "/api/v1/status", (req, res) => {
    json(res, 200, {
        status:    "ok",
        version:   "1.0.0",
        engine:    "node",
        timestamp: new Date().toISOString(),
        cbx_root:  CBX_ROOT,
    });
});

route("GET", "/api/v1/hardware", (req, res) => {
    json(res, 200, loadHardware());
});

route("GET", "/api/v1/builds", (req, res) => {
    const buildsDir = path.join(CBX_ROOT, "builds");
    const builds    = [];
    if (fs.existsSync(buildsDir)) {
        for (const name of fs.readdirSync(buildsDir).sort().reverse()) {
            const bPath  = path.join(buildsDir, name);
            const mPath  = path.join(bPath, "manifest.json");
            if (fs.statSync(bPath).isDirectory()) {
                let manifest = {};
                if (fs.existsSync(mPath)) {
                    try { manifest = JSON.parse(fs.readFileSync(mPath, "utf8")); }
                    catch (_) {}
                }
                builds.push({ name, ...manifest });
            }
        }
    }
    json(res, 200, { builds, count: builds.length });
});

route("GET", "/api/v1/modules", (req, res) => {
    const modsDir = path.join(CBX_ROOT, "modules");
    const modules = [];
    if (fs.existsSync(modsDir)) {
        for (const name of fs.readdirSync(modsDir).sort()) {
            const mPath = path.join(modsDir, name);
            if (fs.statSync(mPath).isDirectory()) {
                const scripts = fs.readdirSync(mPath).filter(f => f.endsWith(".sh"));
                modules.push({ name, scripts });
            }
        }
    }
    json(res, 200, { modules });
});

route("GET", "/api/v1/logs", (req, res) => {
    let lines = [];
    if (fs.existsSync(LOG_FILE)) {
        lines = fs.readFileSync(LOG_FILE, "utf8")
            .split("\n").filter(Boolean).slice(-100);
    }
    json(res, 200, { log: lines });
});

route("POST", "/api/v1/run", (req, res, body) => {
    const allowed = new Set(["hardware", "build", "test", "sim", "vcloud", "vm", "update"]);
    let data = {};
    try { data = JSON.parse(body); } catch (_) {}
    const cmd = data.command || "";

    if (!allowed.has(cmd)) {
        return json(res, 400, { error: `Command not allowed: ${cmd}` });
    }

    const scriptMap = {
        hardware: path.join(CBX_ROOT, "modules", "hardware", "detect.sh"),
        build:    path.join(CBX_ROOT, "modules", "os_builder", "blueprint.sh"),
        test:     path.join(CBX_ROOT, "modules", "os_tester",  "integrity.sh"),
        sim:      path.join(CBX_ROOT, "modules", "boot_sim",   "simulate.sh"),
        vcloud:   path.join(CBX_ROOT, "modules", "vcloud",     "build.sh"),
        vm:       path.join(CBX_ROOT, "modules", "vm",         "lite_vm.sh"),
        update:   path.join(CBX_ROOT, "modules", "updater",    "self_upgrade.sh"),
    };

    const script = scriptMap[cmd];
    if (!script || !fs.existsSync(script)) {
        return json(res, 404, { error: "Script not found" });
    }

    const env = { ...process.env, CBX_ROOT, CBX_NO_COLOR: "1" };
    execFile("bash", [script], { env, timeout: 60000 }, (err, stdout, stderr) => {
        json(res, 200, {
            command:    cmd,
            returncode: err ? (err.code || 1) : 0,
            stdout:     stdout.slice(-4096),
            stderr:     stderr.slice(-1024),
        });
    });
});

// ---- Site Builder helpers ---------------------------------------------------
function sitesDir() {
    return path.join(CBX_ROOT, "data", "sites");
}

function readManifest(name) {
    const p = path.join(sitesDir(), name, "manifest.json");
    if (!fs.existsSync(p)) return null;
    try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch (_) { return null; }
}

function writeManifest(name, manifest) {
    const p = path.join(sitesDir(), name, "manifest.json");
    fs.writeFileSync(p, JSON.stringify(manifest, null, 2));
}

function safeName(name) {
    return (name || "").replace(/[^a-zA-Z0-9_\-]/g, "");
}

// ---- Site Builder routes ----------------------------------------------------
route("GET", "/api/v1/sites", (req, res) => {
    const dir   = sitesDir();
    const sites = [];
    if (fs.existsSync(dir)) {
        for (const entry of fs.readdirSync(dir).sort().reverse()) {
            const m = readManifest(entry);
            if (m) sites.push(m);
        }
        sites.sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
    }
    json(res, 200, { sites, count: sites.length });
});

route("POST", "/api/v1/sites", (req, res, body) => {
    let data = {};
    try { data = JSON.parse(body); } catch (_) {}
    const name = safeName(data.name || "");
    if (!name) return json(res, 400, { error: "name is required" });

    const projectDir = path.join(sitesDir(), name);
    if (fs.existsSync(projectDir)) {
        return json(res, 409, { error: `Site '${name}' already exists.` });
    }

    const templates = ["blank", "landing", "portfolio", "blog"];
    const template  = templates.includes(data.template) ? data.template : "landing";
    const modes     = ["template", "code"];
    const mode      = modes.includes(data.mode) ? data.mode : "template";
    const title     = data.title || name.replace(/[-_]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    const desc      = data.description || `${title} — built with CoreBuilderVX Website Builder.`;

    try {
        fs.mkdirSync(path.join(projectDir, "pages"),  { recursive: true });
        fs.mkdirSync(path.join(projectDir, "assets"), { recursive: true });
        fs.mkdirSync(path.join(projectDir, "_build"), { recursive: true });
    } catch (e) {
        return json(res, 500, { error: "Could not create project directories" });
    }

    const now      = new Date().toISOString();
    const manifest = { name, template, mode, title, description: desc,
                       created_at: now, updated_at: now, last_build: null,
                       pages: ["index"] };
    writeManifest(name, manifest);

    // Write a minimal starter page
    const starterHtml = `<!DOCTYPE html>\n<html lang="en">\n<head>\n` +
        `  <meta charset="UTF-8">\n  <title>${title}</title>\n</head>\n<body>\n` +
        `  <h1>${title}</h1>\n  <p>${desc}</p>\n` +
        `  <footer>Built with CoreBuilderVX</footer>\n</body>\n</html>\n`;
    fs.writeFileSync(path.join(projectDir, "pages", "index.html"), starterHtml);

    json(res, 201, manifest);
});

route("GET", "/api/v1/sites/:name", (req, res) => {
    // handled via the dynamic router below
});

route("POST", "/api/v1/sites/:name/build", (req, res) => {
    // handled via the dynamic router below
});

route("DELETE", "/api/v1/sites/:name", (req, res) => {
    // handled via the dynamic router below
});

// ---- Serve cockpit UI -------------------------------------------------------
route("GET", "/", (req, res) => {
    const cockpitPath = path.join(CBX_ROOT, "modules", "frontend", "cockpit.html");
    if (fs.existsSync(cockpitPath)) {
        const body = fs.readFileSync(cockpitPath);
        res.writeHead(200, { "Content-Type": "text/html" });
        res.end(body);
    } else {
        json(res, 200, { message: "CoreBuilderVX API", version: "1.0.0" });
    }
});

// ---- HTTP server ------------------------------------------------------------
// ---- HTTP server ------------------------------------------------------------
// Dynamic route handlers for parameterised paths
function _handleDynamic(method, url, req, res, body) {
    // GET /api/v1/sites/<name>
    let m = url.match(/^\/api\/v1\/sites\/([^/]+)$/);
    if (m && method === "GET") {
        const name     = safeName(m[1]);
        const manifest = readManifest(name);
        if (!manifest) return json(res, 404, { error: `Site '${name}' not found` });
        return json(res, 200, manifest);
    }
    // POST /api/v1/sites/<name>/build
    m = url.match(/^\/api\/v1\/sites\/([^/]+)\/build$/);
    if (m && method === "POST") {
        const name    = safeName(m[1]);
        const pDir    = path.join(sitesDir(), name);
        if (!fs.existsSync(pDir)) return json(res, 404, { error: `Site '${name}' not found` });
        const buildDir  = path.join(pDir, "_build");
        const pagesDir  = path.join(pDir, "pages");
        const assetsDir = path.join(pDir, "assets");
        if (fs.existsSync(buildDir))
            fs.rmSync(buildDir, { recursive: true });
        fs.mkdirSync(buildDir, { recursive: true });
        if (fs.existsSync(pagesDir)) {
            for (const f of fs.readdirSync(pagesDir)) {
                if (f.endsWith(".html"))
                    fs.copyFileSync(path.join(pagesDir, f), path.join(buildDir, f));
            }
        }
        if (fs.existsSync(assetsDir) && fs.readdirSync(assetsDir).length) {
            const copyDir = (src, dst) => {
                fs.mkdirSync(dst, { recursive: true });
                for (const e of fs.readdirSync(src)) {
                    const s = path.join(src, e), d = path.join(dst, e);
                    fs.statSync(s).isDirectory() ? copyDir(s, d) : fs.copyFileSync(s, d);
                }
            };
            copyDir(assetsDir, path.join(buildDir, "assets"));
        }
        const now      = new Date().toISOString();
        const manifest = readManifest(name) || {};
        manifest.updated_at = now;
        manifest.last_build = now;
        writeManifest(name, manifest);
        return json(res, 200, { status: "ok", build_dir: buildDir, manifest });
    }
    // DELETE /api/v1/sites/<name>
    m = url.match(/^\/api\/v1\/sites\/([^/]+)$/);
    if (m && method === "DELETE") {
        const name = safeName(m[1]);
        const pDir = path.join(sitesDir(), name);
        if (!fs.existsSync(pDir)) return json(res, 404, { error: `Site '${name}' not found` });
        fs.rmSync(pDir, { recursive: true });
        return json(res, 200, { status: "ok", deleted: name });
    }
    return false;
}

const server = http.createServer((req, res) => {
    if (req.method === "OPTIONS") {
        res.writeHead(204, {
            "Access-Control-Allow-Origin":  "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        });
        return res.end();
    }

    let body = "";
    req.on("data", d => { body += d; });
    req.on("end", () => {
        const key  = `${req.method} ${req.url.split("?")[0]}`;
        // routes is created with Object.create(null) so has no prototype chain;
        // safe to index directly — check is type-guard only
        const handler = routes[key];
        if (typeof handler === "function") {
            handler(req, res, body);
        } else if (!_handleDynamic(req.method, req.url.split("?")[0], req, res, body)) {
            json(res, 404, { error: `Not found: ${req.url}` });
        }
    });
});

server.listen(API_PORT, API_HOST, () => {
    console.log(`[CBX-API] Node.js backend running at http://${API_HOST}:${API_PORT}`);
});
