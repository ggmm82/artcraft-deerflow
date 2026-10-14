#!/usr/bin/env bash
set -euo pipefail
export STUDIO_PASSWORD=ci-only-not-a-real-credential-123456
export STUDIO_BIND_IP=127.0.0.1
export STUDIO_PUBLIC_URL=http://localhost:2026
cleanup() {
  docker compose logs --no-color --tail=100 gateway frontend proxy || true
  docker compose down -v || true
}
trap cleanup EXIT
docker compose up -d --no-build
for attempt in $(seq 1 60); do
  if curl -fsS --user "admin:$STUDIO_PASSWORD" http://127.0.0.1:2026/health/ready >/dev/null; then
    break
  fi
  sleep 2
done
curl -fsS --user "admin:$STUDIO_PASSWORD" http://127.0.0.1:2026/health/ready
curl -fsS --user "admin:$STUDIO_PASSWORD" http://127.0.0.1:2026/ >/dev/null
test "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:2026/studio/)" = 401
# Studio is inside DeerFlow: before app login it may require the DeerFlow session.
status="$(curl -s -o /tmp/studio-http -w '%{http_code}' --user "admin:$STUDIO_PASSWORD" http://127.0.0.1:2026/studio/)"
case "$status" in
  200) grep -q 'ArtCraft Studio' /tmp/studio-http ;;
  401|403) echo 'DeerFlow requires its authenticated account before opening Studio' ;;
  *) cat /tmp/studio-http; exit 1 ;;
esac
python scripts/ci_http.py
