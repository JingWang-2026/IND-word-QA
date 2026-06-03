$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$backend = Join-Path $root "backend"

Set-Location $backend
$env:WORD_QA_BACKEND_PORT = "8011"
$env:WORD_QA_FRONTEND_PORT = "5175"
$env:WORD_QA_FRONTEND_ORIGINS = "http://localhost:5175,http://127.0.0.1:5175"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
