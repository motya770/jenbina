#!/usr/bin/env bash
# Start Jenbina's private Minecraft server. Stop it with Ctrl-C or by typing "stop".
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$HERE/server"

[ -f "$SERVER_DIR/server.jar" ] || { echo "Run ./minecraft/setup_server.sh first." >&2; exit 1; }
grep -qs '^eula=true' "$SERVER_DIR/eula.txt" || {
  echo "The Minecraft EULA is not accepted yet. See ./minecraft/setup_server.sh." >&2
  exit 1
}

cd "$SERVER_DIR"
exec java -Xms1G -Xmx2G -jar server.jar nogui
