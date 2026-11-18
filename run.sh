#!/usr/bin/env sh
cd "$(dirname "$0")"
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
cd frontend
npm run dev
