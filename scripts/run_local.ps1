$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Virtual environment not found. Create .venv and install requirements first."
}

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/version" -TimeoutSec 2 | Out-Null
} catch {
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        throw "Ollama is not installed or is not available on PATH."
    }
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    for ($Attempt = 0; $Attempt -lt 20; $Attempt++) {
        Start-Sleep -Seconds 1
        try {
            Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/version" -TimeoutSec 2 | Out-Null
            break
        } catch {
            if ($Attempt -eq 19) { throw "Ollama did not become ready in time." }
        }
    }
}

Set-Location $ProjectRoot
& $Python -m streamlit run app.py
