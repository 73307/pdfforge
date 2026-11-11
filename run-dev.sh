#!/usr/bin/env bash
# Script to run both backend and frontend locally.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Reliably free a TCP port: try a graceful kill, then force, and verify.
free_port() {
  local port="$1" pids
  for _ in 1 2 3; do
    pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    [ -z "$pids" ] && return 0
    echo "⚠️  Port $port is in use (PID: $pids). Freeing it up..."
    kill $pids 2>/dev/null || true
    sleep 1
    pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    [ -z "$pids" ] && return 0
    kill -9 $pids 2>/dev/null || true
    sleep 1
  done
  pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "❌ Could not free port $port (PID: $pids). Close that process and try again."
    exit 1
  fi
}

# Free backend (8000) and frontend (3000) ports before starting.
free_port 8000
free_port 3000

# Verify backend virtualenv
if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
  echo "❌ Backend .venv not found. Creating virtual environment..."
  python3 -m venv "$ROOT_DIR/backend/.venv"
  "$ROOT_DIR/backend/.venv/bin/pip" install --upgrade pip
  "$ROOT_DIR/backend/.venv/bin/pip" install -r "$ROOT_DIR/backend/requirements.txt"
fi

# Verify frontend dependencies
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "❌ frontend/node_modules not found. Running npm install..."
  (cd "$ROOT_DIR/frontend" && npm install)
fi

# Ensure frontend .env.local exists
if [ ! -f "$ROOT_DIR/frontend/.env.local" ]; then
  echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > "$ROOT_DIR/frontend/.env.local"
fi

# Ensure backend .env exists
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/backend/.env"
fi

# Enable the admin dashboard locally (dev only). Export your own ADMIN_PASSWORD before
# running to override. Production sets its own values in docker-compose.prod.yml.
export ADMIN_USER="${ADMIN_USER:-admin}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-devadmin}"

echo "🚀 Starting PDFForge Backend (http://localhost:8000)..."
echo "🔐 Admin dashboard: http://localhost:8000/admin  (user: $ADMIN_USER · pass: $ADMIN_PASSWORD)"
# `exec` replaces the subshell with uvicorn, so $BACKEND_PID is uvicorn itself
# and the cleanup below can actually stop it (no orphan left holding port 8000).
(cd "$ROOT_DIR/backend" && exec .venv/bin/uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

cleanup() {
  echo ""
  echo "🛑 Shutting down PDFForge services..."
  kill "$BACKEND_PID" 2>/dev/null || true
  # Backstop: make sure nothing is left holding either port.
  for p in $(lsof -ti tcp:8000 2>/dev/null || true) $(lsof -ti tcp:3000 2>/dev/null || true); do
    kill -9 "$p" 2>/dev/null || true
  done
  exit 0
}

trap cleanup INT TERM EXIT

echo "🚀 Starting PDFForge Frontend (http://localhost:3000)..."
(cd "$ROOT_DIR/frontend" && npm run dev)
