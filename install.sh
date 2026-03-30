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
echo "Installed!"
echo "Installerat: $BIN_DIR/wlauncher"
echo "Add to Hyprland-configuration -"
echo "Lägg till i Hyprland-config (hyprland.conf):"
echo '  bind = SUPER, R, exec, wlauncher'
echo "Make sure that it is in a PATH that hyprland can find! sometimes ~/.local/bin isnt enough. then copy it manually to /usr/bin "
echo "Se till att ~/.local/bin är i din PATH."
echo ""
