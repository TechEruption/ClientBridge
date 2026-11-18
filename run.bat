@echo off
start "ClientBridge Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
start "ClientBridge Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
