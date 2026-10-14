#!/bin/sh
set -eu
export BETTER_AUTH_SECRET="$(node -e 'process.stdout.write(require("crypto").createHash("sha256").update(process.env.STUDIO_PASSWORD).digest("hex"))')"
unset STUDIO_PASSWORD
cd /app/frontend
exec pnpm start
