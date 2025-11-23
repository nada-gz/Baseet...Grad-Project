# PowerShell script to start the backend server
Set-Location $PSScriptRoot
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000


