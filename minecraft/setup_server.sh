#!/usr/bin/env bash
# Set up Jenbina's private Minecraft server in minecraft/server/.
#
#   ./minecraft/setup_server.sh                 download and configure
#   ./minecraft/setup_server.sh --accept-eula   also accept the Minecraft EULA
#
# The server will not start until the EULA is accepted. Read it first:
# https://www.minecraft.net/en-us/eula
set -euo pipefail

VERSION="1.21.4"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$HERE/server"
MANIFEST_URL="https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

ACCEPT_EULA=0
for arg in "$@"; do
  case "$arg" in
    --accept-eula) ACCEPT_EULA=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

command -v java >/dev/null || { echo "Java 21 or newer is required." >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required." >&2; exit 1; }
mkdir -p "$SERVER_DIR"

if [ ! -f "$SERVER_DIR/server.jar" ]; then
  echo "Downloading the Minecraft $VERSION server from Mojang..."
  # Mojang's manifest names the jar and its checksum; the download is verified against it.
  python3 - "$MANIFEST_URL" "$VERSION" "$SERVER_DIR/server.jar" <<'PY'
import hashlib, json, os, sys, urllib.request

manifest_url, version, destination = sys.argv[1:4]
manifest = json.load(urllib.request.urlopen(manifest_url, timeout=30))
entry = next((v for v in manifest["versions"] if v["id"] == version), None)
if entry is None:
    sys.exit(f"Mojang's manifest has no version {version}.")
server = json.load(urllib.request.urlopen(entry["url"], timeout=30))["downloads"]["server"]
partial = destination + ".part"
urllib.request.urlretrieve(server["url"], partial)
digest = hashlib.sha1(open(partial, "rb").read()).hexdigest()
if digest != server["sha1"]:
    os.remove(partial)
    sys.exit("The downloaded server did not match Mojang's checksum; nothing was kept.")
os.replace(partial, destination)
print(f"Verified against Mojang's checksum ({digest[:12]}...).")
PY
else
  echo "server.jar is already there; not downloading again."
fi

if [ ! -f "$SERVER_DIR/server.properties" ]; then
  cat > "$SERVER_DIR/server.properties" <<'EOF'
# Jenbina's private world. Reachable from this machine only.
server-ip=127.0.0.1
server-port=25565
# Offline mode lets her join without a Microsoft account. Keep server-ip local.
online-mode=false
enforce-secure-profile=false
motd=Jenbina's world
max-players=5
gamemode=survival
# Easy gives her a body that gets hungry. Monsters are off: with them on she
# is attacked at night and loses what she carries when she dies.
difficulty=easy
spawn-monsters=false
view-distance=8
simulation-distance=6
# The world waits for her between beats.
pause-when-empty-seconds=10
EOF
  echo "Wrote server.properties."
else
  echo "server.properties is already there; left as it is."
fi

if [ "$ACCEPT_EULA" = 1 ]; then
  printf 'eula=true\n' > "$SERVER_DIR/eula.txt"
  echo "Recorded your acceptance of the Minecraft EULA."
elif [ ! -f "$SERVER_DIR/eula.txt" ]; then
  echo
  echo "The server needs you to accept the Minecraft EULA before it will start:"
  echo "  https://www.minecraft.net/en-us/eula"
  echo "Run this script again with --accept-eula once you have read it."
fi

echo
echo "Start the world with:  ./minecraft/run_server.sh"
