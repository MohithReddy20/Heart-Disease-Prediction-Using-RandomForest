#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/frontend"
npm ci
npm run build
cd "$ROOT"
rm -rf "$ROOT/p1_heartdiseaseprediction/static/spa"
mkdir -p "$ROOT/p1_heartdiseaseprediction/static/spa"
cp -R "$ROOT/frontend/dist/." "$ROOT/p1_heartdiseaseprediction/static/spa/"
echo "SPA copied to p1_heartdiseaseprediction/static/spa/"
