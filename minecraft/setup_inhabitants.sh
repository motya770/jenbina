#!/usr/bin/env bash
# Set up the others who live in Jenbina's Minecraft world: Mira and Tobin,
# played by Mindcraft (https://github.com/mindcraft-bots/mindcraft).
#
#   ./minecraft/setup_inhabitants.sh
#
# Mindcraft is someone else's program. This downloads it into
# minecraft/mindcraft/ at one fixed commit and installs its packages; nothing
# of it is changed or committed here. Safe to run again.
#
# Her mind starts and stops the inhabitants with her world. They need
# OPENAI_API_KEY in the environment her mind is started with.
set -euo pipefail

REPOSITORY="https://github.com/mindcraft-bots/mindcraft"
# The commit that was tried against her world (branch develop, 2026-10-26).
COMMIT="e1c1fc3ffa481506c2445fc639e16dba504b5920"
# Mindcraft's packages build on Node 20; on other versions some do not.
NODE_MAJOR="20"
# Mindcraft patches this exact Mineflayer; a newer one makes its patch fail.
MINEFLAYER="4.33.0"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINDCRAFT_DIR="$HERE/mindcraft"
NODE_DIR="$HERE/mindcraft-node"

command -v git >/dev/null || { echo "git is required." >&2; exit 1; }
command -v npm >/dev/null || { echo "npm (Node) is required." >&2; exit 1; }

if [ ! -d "$MINDCRAFT_DIR/.git" ]; then
  echo "Downloading Mindcraft into minecraft/mindcraft/ ..."
  git clone --quiet "$REPOSITORY" "$MINDCRAFT_DIR"
fi
# Her mind starts the inhabitants only when this file exists; it is written
# again as the last step, so a setup that stops half-way is not started.
rm -f "$MINDCRAFT_DIR/.jenbina-ready"
if [ "$(git -C "$MINDCRAFT_DIR" rev-parse HEAD)" != "$COMMIT" ]; then
  git -C "$MINDCRAFT_DIR" fetch --quiet origin "$COMMIT" 2>/dev/null || git -C "$MINDCRAFT_DIR" fetch --quiet origin
  git -C "$MINDCRAFT_DIR" -c advice.detachedHead=false checkout --quiet "$COMMIT"
fi
echo "Mindcraft is at $(git -C "$MINDCRAFT_DIR" rev-parse --short HEAD)."

# Use this machine's Node when it is the right one; otherwise a private copy.
if [ "$(node --version 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/')" != "$NODE_MAJOR" ]; then
  if [ ! -x "$NODE_DIR/node_modules/node/bin/node" ]; then
    echo "This machine's Node is not version $NODE_MAJOR; installing a private one into minecraft/mindcraft-node/ ..."
    mkdir -p "$NODE_DIR"
    npm install --prefix "$NODE_DIR" --no-audit --no-fund --loglevel=error "node@$NODE_MAJOR"
  fi
  export PATH="$NODE_DIR/node_modules/node/bin:$PATH"
fi
echo "Installing Mindcraft's packages with Node $(node --version) ..."

cd "$MINDCRAFT_DIR"
npm install --no-audit --no-fund --loglevel=error
npm install --no-save --no-audit --no-fund --loglevel=error "mineflayer@$MINEFLAYER"
npx --no-install patch-package
echo "$COMMIT" > "$MINDCRAFT_DIR/.jenbina-ready"

cat <<'DONE'

The inhabitants are set up. Start her mind as usual, for example:

  JENBINA_WORLD=minecraft python run_heartbeat.py

Mira and Tobin join a little after her world is up. What they print goes to
minecraft/logs/inhabitants.log. See "Company" in minecraft/README.md.
DONE
