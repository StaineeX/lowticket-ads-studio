$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$stdout = Join-Path $env:TEMP "lowticket-ads-studio-smoke-out.log"
$stderr = Join-Path $env:TEMP "lowticket-ads-studio-smoke-err.log"

if (-not (Test-Path -LiteralPath $python)) {
  throw "Python virtual environment not found at $python"
}

$server = Start-Process -FilePath $python -ArgumentList @(
  "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8765"
) -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr

try {
  Start-Sleep -Seconds 2
  $health = Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/health"
  if ($health.status -ne "ok") { throw "Health check failed" }

  $body = @{
    offer_name = "Smoke Course"
    benefit = "Learn a practical skill"
    audience = "beginners"
    proof = "short lessons"
    cta = "Start now"
    price = "47"
    currency = "BRL"
    budget = "20"
    platforms = @("meta")
  } | ConvertTo-Json
  $draft = Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/campaign-drafts/generate" -Method Post -ContentType "application/json" -Body $body
  if ($draft.status -ne "paused") { throw "Draft was not paused" }
  Write-Output "Smoke OK: health and paused campaign draft verified."
}
finally {
  if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force }
  Remove-Item -LiteralPath $stdout, $stderr -Force -ErrorAction SilentlyContinue
}
