$ErrorActionPreference = "Stop"

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama is not installed or is not available on PATH."
}

Write-Host "Pulling the chat model..." -ForegroundColor Cyan
ollama pull llama3.2:3b

Write-Host "Pulling the embedding model..." -ForegroundColor Cyan
ollama pull nomic-embed-text

Write-Host "Models are ready." -ForegroundColor Green
