import {
  checkPortOpen,
  config,
  fail,
  fetchJson,
  fetchText,
  fileExists,
  firstConfiguredApiBaseUrl,
  info,
  pass,
  warn,
} from "./local-config.mjs";

const mode = process.argv[2] || "all";
const failures = [];

function recordFail(message) {
  failures.push(message);
  fail(message);
}

async function checkEnv() {
  info("Checking environment files");
  const rootEnvOk = fileExists(".env") || fileExists(".env.example");
  const frontendEnvOk = fileExists("frontend/.env.local") || fileExists("frontend/.env") || fileExists("frontend/.env.example");
  if (rootEnvOk) pass("Root .env or .env.example exists.");
  else recordFail("Missing root .env or .env.example. Create .env.example with fixed local ports.");

  if (frontendEnvOk) pass("Frontend .env.local/.env/.env.example exists.");
  else recordFail("Missing frontend env file. Create frontend/.env.local with VITE_API_BASE_URL.");

  const apiBase = firstConfiguredApiBaseUrl();
  if (apiBase.value === config.expectedApiBaseUrl) {
    pass(`VITE_API_BASE_URL is ${apiBase.value} (${apiBase.source}).`);
  } else {
    recordFail(
      `VITE_API_BASE_URL is ${apiBase.value || "not configured"} (${apiBase.source || "no env file"}). Expected ${config.expectedApiBaseUrl}.`,
    );
  }
}

async function checkPorts() {
  info("Checking fixed local ports");
  const frontendOpen = await checkPortOpen(config.frontendPort);
  const backendOpen = await checkPortOpen(config.backendPort);

  if (frontendOpen) pass(`Frontend port ${config.frontendPort} is open.`);
  else recordFail(`Frontend port ${config.frontendPort} is not open. Start it with npm run dev from the project root.`);

  if (backendOpen) pass(`Backend port ${config.backendPort} is open.`);
  else recordFail(`Backend port ${config.backendPort} is not open. Start it with scripts/start-backend.ps1 or npm run dev.`);
}

async function checkHealth() {
  info("Checking backend /health");
  try {
    const { response, json } = await fetchJson(`${config.backendUrl}/health`);
    if (!response.ok) {
      recordFail(`Backend /health returned HTTP ${response.status}.`);
      return;
    }
    if (json.status === "ok") {
      pass("Backend /health returned status: ok.");
    } else if (json.status) {
      warn(`Backend /health returned status: ${json.status}. This is explainable, inspect details below.`);
    } else {
      recordFail("Backend /health did not include a status field.");
    }
    if (json.service === config.serviceName) pass(`Backend service is ${json.service}.`);
    else recordFail(`Backend service is ${json.service || "missing"}. Expected ${config.serviceName}.`);
    if (json.port === config.backendPort) pass(`Backend reports port ${json.port}.`);
    else recordFail(`Backend reports port ${json.port}. Expected ${config.backendPort}.`);
    if (json.database?.status === "connected") pass("Database is connected.");
    else warn(`Database status: ${json.database?.status || "missing"}. Error: ${json.database?.error || "none"}`);
    if (json.upload_storage?.writable) pass("Upload storage exists and is writable.");
    else warn(`Upload storage is not writable. Error: ${json.upload_storage?.error || "none"}`);
  } catch (error) {
    recordFail(`Cannot reach ${config.backendUrl}/health. ${error.message}`);
    info(`Suggestion: start backend with scripts/start-backend.ps1 and confirm ${config.backendUrl}/health opens.`);
  }
}

async function checkFrontend() {
  info("Checking frontend page");
  try {
    const { response, text } = await fetchText(config.frontendUrl);
    if (!response.ok) {
      recordFail(`Frontend returned HTTP ${response.status} at ${config.frontendUrl}.`);
      return;
    }
    pass(`Frontend is reachable at ${config.frontendUrl}.`);
    if (text.includes(config.serviceName)) pass(`Frontend page contains software name: ${config.serviceName}.`);
    else recordFail(`Frontend page does not contain software name: ${config.serviceName}. You may be opening the wrong app.`);
  } catch (error) {
    recordFail(`Cannot reach frontend at ${config.frontendUrl}. ${error.message}`);
    info(`Suggestion: start frontend with scripts/start-frontend.ps1 or npm run dev from the project root.`);
  }
}

async function main() {
  console.log(`Local check mode: ${mode}`);
  console.log(`Expected frontend: ${config.frontendUrl}`);
  console.log(`Expected backend:  ${config.backendUrl}`);

  if (mode === "ports") {
    await checkPorts();
  } else if (mode === "health") {
    await checkHealth();
  } else if (mode === "all") {
    await checkEnv();
    await checkPorts();
    await checkHealth();
    await checkFrontend();
  } else {
    recordFail(`Unknown check mode "${mode}". Use all, ports, or health.`);
  }

  if (failures.length > 0) {
    console.error("");
    console.error(`Local check failed with ${failures.length} issue(s):`);
    for (const item of failures) console.error(`- ${item}`);
    process.exit(1);
  }

  console.log("");
  console.log("Local check passed.");
}

main().catch((error) => {
  console.error(`FAIL  Local check crashed unexpectedly: ${error.message}`);
  process.exit(1);
});
