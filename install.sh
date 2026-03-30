#!/usr/bin/env bash
# Installerar wlauncher till ~/.local/bin och kopierar defaultkonfig

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
CONF_DIR="$HOME/.config/wlauncher"

mkdir -p "$BIN_DIR" "$CONF_DIR"

# Kopiera körbar
cp "$SCRIPT_DIR/launcher.py" "$BIN_DIR/wlauncher"
chmod +x "$BIN_DIR/wlauncher"

# Kopiera defaultkonfig om ingen finns
if [ ! -f "$CONF_DIR/config.ini" ]; then
    cp "$SCRIPT_DIR/config.ini" "$CONF_DIR/config.ini"
    echo "Konfigfil skapad: $CONF_DIR/config.ini"
else
    echo "Konfigfil finns redan: $CONF_DIR/config.ini (ingen ändring)"
fi

echo "Installerat: $BIN_DIR/wlauncher"
echo ""
echo "Lägg till i Hyprland-konfig (hyprland.conf):"
echo '  bind = SUPER, R, exec, wlauncher'
echo ""
echo "Se till att ~/.local/bin är i din PATH."
