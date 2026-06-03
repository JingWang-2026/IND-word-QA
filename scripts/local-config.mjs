import fs from "node:fs";
import net from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const rootDir = path.resolve(__dirname, "..");

export const config = {
  serviceName: "Word Report QA Assistant",
  frontendPort: 5175,
  backendPort: 8011,
  frontendUrl: "http://localhost:5175",
  backendUrl: "http://127.0.0.1:8011",
  expectedApiBaseUrl: "http://127.0.0.1:8011",
};

export function readEnvFile(relativePath) {
  const filePath = path.join(rootDir, relativePath);
  if (!fs.existsSync(filePath)) return null;
  const values = {};
  for (const rawLine of fs.readFileSync(filePath, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const index = line.indexOf("=");
    if (index === -1) continue;
    values[line.slice(0, index).trim()] = line.slice(index + 1).trim();
  }
  return { filePath, values };
}

export function firstConfiguredApiBaseUrl() {
  const sources = [
    "frontend/.env.local",
    "frontend/.env",
    "frontend/.env.example",
    ".env",
    ".env.example",
  ];
  for (const source of sources) {
    const env = readEnvFile(source);
    if (env?.values.VITE_API_BASE_URL) {
      return { source, value: env.values.VITE_API_BASE_URL };
    }
  }
  return { source: null, value: null };
}

export function fileExists(relativePath) {
  return fs.existsSync(path.join(rootDir, relativePath));
}

export function checkPortOpen(port, host = "127.0.0.1", timeoutMs = 1500) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    let settled = false;
    const done = (open) => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve(open);
    };
    socket.setTimeout(timeoutMs);
    socket.once("connect", () => done(true));
    socket.once("timeout", () => done(false));
    socket.once("error", () => done(false));
    socket.connect(port, host);
  });
}

export async function fetchText(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  return { response, text };
}

export async function fetchJson(url, options = {}) {
  const { response, text } = await fetchText(url, options);
  let json = null;
  try {
    json = JSON.parse(text);
  } catch {
    throw new Error(`${url} did not return valid JSON. HTTP ${response.status}. Body: ${text.slice(0, 200)}`);
  }
  return { response, json };
}

export function pass(message) {
  console.log(`PASS  ${message}`);
}

export function warn(message) {
  console.log(`WARN  ${message}`);
}

export function fail(message) {
  console.error(`FAIL  ${message}`);
}

export function info(message) {
  console.log(`INFO  ${message}`);
}
