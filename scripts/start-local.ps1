$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

$env:WORD_QA_FRONTEND_ORIGINS = "http://localhost:5175,http://127.0.0.1:5175"
$env:WORD_QA_BACKEND_PORT = "8011"
$env:WORD_QA_FRONTEND_PORT = "5175"
$env:VITE_API_BASE_URL = "http://127.0.0.1:8011"

Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8011") -WorkingDirectory $backend -WindowStyle Hidden
Start-Sleep -Seconds 3
Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "dev") -WorkingDirectory $frontend -WindowStyle Hidden

Write-Host "Word Report QA Assistant started"
Write-Host "Frontend: http://localhost:5175"
Write-Host "Backend:  http://127.0.0.1:8011"
Write-Host "Health:   http://127.0.0.1:8011/health"
