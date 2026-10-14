#!/bin/sh
set -eu
: "${STUDIO_PASSWORD:?Impostare STUDIO_PASSWORD in Hostinger}"
export STUDIO_USER="${STUDIO_USER:-admin}"
export STUDIO_PASSWORD_HASH="$(caddy hash-password --plaintext "$STUDIO_PASSWORD")"
unset STUDIO_PASSWORD
exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
