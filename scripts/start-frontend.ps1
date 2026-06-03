$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$frontend = Join-Path $root "frontend"

Set-Location $frontend
$env:VITE_API_BASE_URL = "http://127.0.0.1:8011"
npm run dev
