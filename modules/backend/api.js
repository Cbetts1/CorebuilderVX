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

// ---- Input sanitisation -----------------------------------------------------
/** Strip any character that is not alphanumeric, hyphen, or underscore.
 *  Used to prevent command-line injection for user-supplied project/template names.
 */
function _sanitiseIdentifier(value) {
    return String(value).replace(/[^A-Za-z0-9_\-]/g, "").slice(0, 64);
}

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

route("GET", "/api/v1/sites", (req, res) => {
    const indexPath = path.join(CBX_ROOT, "builds", "websites", "index.json");
    let projects = [];
    if (fs.existsSync(indexPath)) {
        try { projects = JSON.parse(fs.readFileSync(indexPath, "utf8")); } catch (_) {}
    }
    json(res, 200, { sites: projects, count: projects.length });
});

route("GET", "/api/v1/sites/templates", (req, res) => {
    const templatesDir = path.join(CBX_ROOT, "modules", "site_builder", "templates");
    const templates = [];
    if (fs.existsSync(templatesDir)) {
        for (const name of fs.readdirSync(templatesDir).sort()) {
            const tPath = path.join(templatesDir, name);
            if (fs.statSync(tPath).isDirectory()) {
                const files = fs.readdirSync(tPath);
                templates.push({ name, files });
            }
        }
    }
    json(res, 200, { templates });
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
    const allowed = new Set(["hardware", "build", "test", "sim", "vcloud", "vm", "update",
                             "site_create", "site_open", "site_preview"]);
    let data = {};
    try { data = JSON.parse(body); } catch (_) {}
    const cmd = data.command || "";

    if (!allowed.has(cmd)) {
        return json(res, 400, { error: `Command not allowed: ${cmd}` });
    }

    // Site builder commands run website_builder.py
    if (cmd === "site_create" || cmd === "site_open" || cmd === "site_preview") {
        const siteBuilder = path.join(CBX_ROOT, "modules", "site_builder", "website_builder.py");
        if (!fs.existsSync(siteBuilder)) {
            return json(res, 404, { error: "website_builder.py not found" });
        }
        const subCmd = { site_create: "create", site_open: "open", site_preview: "preview" }[cmd];
        // Pass user-supplied values via environment variables, not command-line args,
        // to avoid any command-line injection risk.
        const extraEnv = {};
        if (cmd === "site_create") {
            if (data.name)     extraEnv["CBX_SITE_NAME"]     = _sanitiseIdentifier(String(data.name));
            if (data.template) extraEnv["CBX_SITE_TEMPLATE"] = _sanitiseIdentifier(String(data.template));
        } else if (data.name) {
            extraEnv["CBX_SITE_NAME"] = _sanitiseIdentifier(String(data.name));
        }
        const env = { ...process.env, CBX_ROOT, CBX_NO_COLOR: "1", ...extraEnv };
        execFile("python3", [siteBuilder, subCmd],
            { env, timeout: 30000 },
            (err, stdout, stderr) => {
                json(res, 200, {
                    command:    cmd,
                    returncode: err ? (err.code || 1) : 0,
                    stdout:     stdout.slice(-4096),
                    stderr:     stderr.slice(-1024),
                });
            }
        );
        return;
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
        } else {
            json(res, 404, { error: `Not found: ${req.url}` });
        }
    });
});

server.listen(API_PORT, API_HOST, () => {
    console.log(`[CBX-API] Node.js backend running at http://${API_HOST}:${API_PORT}`);
});
