#!/usr/bin/env sh

export $(cat .env)
python -m uvicorn app.main:app --host 0.0.0.0 --port 3000