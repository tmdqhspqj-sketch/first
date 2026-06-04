Set-Location "$PSScriptRoot\..\erp\backend"
$env:PYTHONPATH = "."
if (-not (Test-Path .\.venv)) { python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt }
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
