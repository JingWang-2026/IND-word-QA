import { config, fail, fetchJson, fetchText, firstConfiguredApiBaseUrl, pass, warn } from "./local-config.mjs";

const failures = [];

function recordFail(message) {
  failures.push(message);
  fail(message);
}

async function main() {
  console.log("Running smoke test");
  console.log(`Frontend: ${config.frontendUrl}`);
  console.log(`Backend:  ${config.backendUrl}`);

  const apiBase = firstConfiguredApiBaseUrl();
  if (apiBase.value !== config.expectedApiBaseUrl) {
    recordFail(`VITE_API_BASE_URL is ${apiBase.value || "not configured"}. Expected ${config.expectedApiBaseUrl}.`);
  } else {
    pass(`VITE_API_BASE_URL is ${apiBase.value}.`);
  }

  try {
    const { response, text } = await fetchText(config.frontendUrl);
    if (!response.ok) recordFail(`Frontend returned HTTP ${response.status}.`);
    else pass("Frontend page can be opened.");

    if (text.includes(config.serviceName)) pass(`Frontend contains software name: ${config.serviceName}.`);
    else recordFail(`Frontend does not contain software name "${config.serviceName}". Check that you opened the right port.`);
  } catch (error) {
    recordFail(`Frontend cannot be opened at ${config.frontendUrl}. ${error.message}`);
  }

  try {
    const origin = config.frontendUrl;
    const { response, json } = await fetchJson(`${config.backendUrl}/health`, { headers: { Origin: origin } });
    if (!response.ok) {
      recordFail(`Backend /health returned HTTP ${response.status}.`);
    } else if (json.status === "ok") {
      pass("Backend /health returned status: ok.");
    } else if (json.status) {
      warn(`Backend returned explainable status: ${json.status}.`);
    } else {
      recordFail("Backend /health did not include status.");
    }

    if (json.service === config.serviceName) pass("Backend service name matches.");
    else recordFail(`Backend service is ${json.service || "missing"}, expected ${config.serviceName}.`);

    const corsOrigin = response.headers.get("access-control-allow-origin");
    if (corsOrigin === origin) pass(`Backend CORS allows frontend origin ${origin}.`);
    else recordFail(`Backend CORS header is ${corsOrigin || "missing"}, expected ${origin}.`);
  } catch (error) {
    recordFail(`Frontend cannot call backend /health at ${config.backendUrl}/health. ${error.message}`);
    console.error(`Hint: start backend with scripts/start-backend.ps1 and verify ${config.backendUrl}/health.`);
  }

  if (failures.length > 0) {
    console.error("");
    console.error(`Smoke test failed with ${failures.length} issue(s):`);
    for (const item of failures) console.error(`- ${item}`);
    process.exit(1);
  }

  console.log("");
  console.log("Smoke test passed.");
}

main().catch((error) => {
  console.error(`FAIL  Smoke test crashed unexpectedly: ${error.message}`);
  process.exit(1);
});
