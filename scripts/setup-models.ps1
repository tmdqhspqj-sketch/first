# Install Ollama models for RTX 4060 8GB + Gemma 4 agent
$ErrorActionPreference = "Stop"
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollama)) {
    Write-Host "Installing Ollama..."
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements --disable-interactivity
}

$root = Split-Path $PSScriptRoot -Parent
$modelfile = Join-Path $root "config\ollama\local-agent.modelfile"

Write-Host "Pulling gemma4:e4b (vision + agent)..."
& $ollama pull gemma4:e4b

Write-Host "Pulling embeddinggemma (RAG)..."
& $ollama pull embeddinggemma

Write-Host "Creating local-agent from Modelfile (num_ctx 8192 for 8GB VRAM)..."
& $ollama create local-agent -f $modelfile

Write-Host "`nInstalled models:"
& $ollama list
