# wlauncher

A fast, minimal application launcher for Wayland compositors — built as a `dmenu`/`dmenu_run` replacement for Hyprland and other wlroots-based tiling window managers.

---

## English

### What it is

wlauncher is a keyboard-driven application launcher that sits in a slim bar at the top or bottom of your screen. Type the first letters of a program name and it filters results instantly. Press Enter to launch. It has no borders, no decorations, and integrates cleanly with your Wayland setup via `gtk-layer-shell`.

A "gay" color mode exists: every character in the results cycles through a full rainbow palette at high speed against a black background.

### Requirements

- Python 3.11+
- GTK 3
- [gtk-layer-shell](https://github.com/wmww/gtk-layer-shell) with GObject Introspection bindings (`python-gobject`)

On Arch Linux:
```bash
sudo pacman -S gtk3 gtk-layer-shell python-gobject
```

On Debian/Ubuntu:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 libgtk-layer-shell-dev gir1.2-gtklayershell-0.1
```

### Installation

```bash
git clone https://github.com/yourusername/wlauncher
cd wlauncher
./install.sh
```

This copies `launcher.py` to `~/.local/bin/wlauncher` and creates a default config at `~/.config/wlauncher/config.ini`. Make sure `~/.local/bin` is in your `$PATH`.

### Hyprland keybind

Add to `~/.config/hypr/hyprland.conf`:

```
bind = SUPER, R, exec, wlauncher
```

### Configuration

The config file lives at `~/.config/wlauncher/config.ini` and is created automatically on first run.

```ini
[colors]
# Hex color code (#rrggbb), "random", or "gay" (animated rainbow)
background = #000000
foreground = #ffffff

[font]
# Font family name — e.g. "JetBrains Mono", "Iosevka", "monospace"
name = monospace
# Size in points
size = 14

[window]
# Where to appear: top or bottom (sits alongside waybar)
position = bottom
# Bar height in pixels
height = 32
# Maximum number of results to display
max_results = 12
```

#### Color options

| Value | Effect |
|-------|--------|
| `#rrggbb` | Fixed hex color |
| `random` | A random color is picked each time the launcher opens |
| `gay` | Foreground only — each character cycles through a full rainbow palette at ~70ms per frame, black background |

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| Type | Filter results instantly (prefix match first, then substring) |
| `Enter` | Launch selected program |
| `Tab` | Complete selected name into the input field |
| `→` / `↓` | Select next result |
| `←` / `↑` | Select previous result (← only when cursor is at start of field) |
| `Esc` | Close without launching |

### Running without gtk-layer-shell

If `gtk-layer-shell` is not installed the launcher falls back to a regular floating window. This is useful for testing on X11 or in environments where the layer shell protocol is unavailable. Full Wayland anchoring and keyboard exclusivity will not work in this mode.

### Compiling to a standalone binary

wlauncher is a Python script and runs without any build step. If you want a single self-contained binary with no Python or GTK runtime dependency at launch time, two options are available.

#### Option 1 — PyInstaller (easiest)

PyInstaller bundles the Python interpreter and all imports into one executable. GTK and `gtk-layer-shell` still need to be present on the system as shared libraries, but no Python installation is required.

```bash
pip install pyinstaller
pyinstaller --onefile --name wlauncher launcher.py
```

The binary ends up in `dist/wlauncher`. Copy it anywhere on your `$PATH`:

```bash
cp dist/wlauncher ~/.local/bin/wlauncher
```

> **Note:** PyInstaller bundles do not include GTK's `.so` files or GObject typelibs. The target machine still needs `gtk3`, `gtk-layer-shell`, and `python-gobject` installed.

#### Option 2 — Nuitka (true native compile)

Nuitka compiles Python source to C and then to a real native binary. This gives faster startup and a smaller footprint than PyInstaller. It requires a C compiler (`gcc` or `clang`) and the Python development headers.

```bash
# Install Nuitka
pip install nuitka

# Install build dependencies (Arch)
sudo pacman -S gcc python

# Compile
python -m nuitka \
    --onefile \
    --output-filename=wlauncher \
    --include-module=gi \
    --include-module=gi.repository.Gtk \
    --include-module=gi.repository.GtkLayerShell \
    --include-module=gi.repository.Gdk \
    --include-module=gi.repository.GLib \
    --include-module=gi.repository.Pango \
    launcher.py
```

This produces a single `wlauncher` binary in the current directory. Copy it to your `$PATH`:

```bash
cp wlauncher ~/.local/bin/wlauncher
```

> **Note:** GObject Introspection loads GTK and layer-shell typelibs at runtime regardless of compile method. The `.typelib` files from `gtk3` and `gtk-layer-shell` must be present on the target system.

#### Which to choose

| | PyInstaller | Nuitka |
|-|------------|--------|
| Build time | Fast (~10 s) | Slow (~1–3 min) |
| Binary size | ~8–15 MB | ~2–5 MB |
| Startup speed | Slightly slower | Faster |
| Requires C compiler | No | Yes |
| True native code | No | Yes |

For most users, running `launcher.py` directly (or via `install.sh`) is the simplest and recommended approach.

---

## Svenska

### Vad det är

wlauncher är en tangentbordsdriven programstartare som visas som ett smalt fält längst upp eller längst ned på skärmen. Skriv de första bokstäverna i ett programnamn och resultaten filtreras direkt. Tryck Enter för att starta. Inga kanter, inga dekorationer — integreras med Wayland via `gtk-layer-shell`.

Det finns ett "gay"-läge: varje tecken i resultatlistan cyklar genom hela regnbågspaletten i hög hastighet mot svart bakgrund.

### Krav

- Python 3.11+
- GTK 3
- [gtk-layer-shell](https://github.com/wmww/gtk-layer-shell) med GObject Introspection-bindningar (`python-gobject`)

På Arch Linux:
```bash
sudo pacman -S gtk3 gtk-layer-shell python-gobject
```

På Debian/Ubuntu:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 libgtk-layer-shell-dev gir1.2-gtklayershell-0.1
```

### Installation

```bash
git clone https://github.com/yourusername/wlauncher
cd wlauncher
./install.sh
```

Skriptet kopierar `launcher.py` till `~/.local/bin/wlauncher` och skapar en standardkonfiguration i `~/.config/wlauncher/config.ini`. Kontrollera att `~/.local/bin` finns i din `$PATH`.

### Hyprland-tangentbindning

Lägg till i `~/.config/hypr/hyprland.conf`:

```
bind = SUPER, R, exec, wlauncher
```

### Konfiguration

Konfigfilen ligger på `~/.config/wlauncher/config.ini` och skapas automatiskt vid första körningen.

```ini
[colors]
# Hexfärg (#rrggbb), "random" eller "gay" (animerad regnbåge)
background = #000000
foreground = #ffffff

[font]
# Typsnittsnamn — t.ex. "JetBrains Mono", "Iosevka", "monospace"
name = monospace
# Storlek i punkter
size = 14

[window]
# Var launchern visas: top eller bottom (intill waybar)
position = bottom
# Höjd i pixlar
height = 32
# Max antal sökresultat
max_results = 12
```

#### Färgalternativ

| Värde | Effekt |
|-------|--------|
| `#rrggbb` | Fast hexfärg |
| `random` | Slumpmässig färg väljs varje gång launchern öppnas |
| `gay` | Endast förgrund — varje tecken cyklar genom hela regnbågspaletten med ~70ms per bildruta, svart bakgrund |

### Tangentbordsgenvägarna

| Tangent | Funktion |
|---------|----------|
| Skriva | Filtrerar direkt (prefix först, sedan delsträng) |
| `Enter` | Startar markerat program |
| `Tab` | Kompletterar markerat namn i inmatningsfältet |
| `→` / `↓` | Nästa resultat |
| `←` / `↑` | Föregående resultat (← bara när markören är i början av fältet) |
| `Esc` | Stäng utan att starta något |

### Utan gtk-layer-shell

Om `gtk-layer-shell` inte är installerat faller launchern tillbaka på ett vanligt flytande fönster. Användbart för testning på X11 eller i miljöer utan layer shell-protokollet. Full Wayland-förankring och tangentbordsexklusivitet fungerar inte i det läget.

### Kompilera till fristående binärfil

wlauncher är ett Python-skript och kräver inget byggsteg. Om du vill ha en enda självständig binärfil utan Python som körtidsberoende finns två alternativ.

#### Alternativ 1 — PyInstaller (enklast)

PyInstaller paketerar Python-tolken och alla importer i en körbar fil. GTK och `gtk-layer-shell` måste fortfarande finnas på systemet som delade bibliotek, men ingen Python-installation krävs.

```bash
pip install pyinstaller
pyinstaller --onefile --name wlauncher launcher.py
```

Binärfilen hamnar i `dist/wlauncher`. Kopiera den till valfri plats i `$PATH`:

```bash
cp dist/wlauncher ~/.local/bin/wlauncher
```

> **Obs:** PyInstaller inkluderar inte GTK:s `.so`-filer eller GObject-typelibs. Målmaskinen behöver fortfarande ha `gtk3`, `gtk-layer-shell` och `python-gobject` installerade.

#### Alternativ 2 — Nuitka (riktig native-kompilering)

Nuitka kompilerar Python-källkoden till C och sedan till en riktig native-binärfil. Det ger snabbare uppstart och ett mindre fotavtryck än PyInstaller. Kräver en C-kompilator (`gcc` eller `clang`) och Python-utvecklingsheaders.

```bash
# Installera Nuitka
pip install nuitka

# Installera byggberoenden (Arch)
sudo pacman -S gcc python

# Kompilera
python -m nuitka \
    --onefile \
    --output-filename=wlauncher \
    --include-module=gi \
    --include-module=gi.repository.Gtk \
    --include-module=gi.repository.GtkLayerShell \
    --include-module=gi.repository.Gdk \
    --include-module=gi.repository.GLib \
    --include-module=gi.repository.Pango \
    launcher.py
```

En enda `wlauncher`-binärfil skapas i aktuell katalog. Kopiera den till `$PATH`:

```bash
cp wlauncher ~/.local/bin/wlauncher
```

> **Obs:** GObject Introspection laddar GTK- och layer-shell-typelibs vid körning oavsett kompileringsmetod. `.typelib`-filerna från `gtk3` och `gtk-layer-shell` måste finnas på målsystemet.

#### Vilket ska man välja?

| | PyInstaller | Nuitka |
|-|------------|--------|
| Byggtid | Snabb (~10 s) | Långsam (~1–3 min) |
| Binärstorlek | ~8–15 MB | ~2–5 MB |
| Uppstartshastighet | Något långsammare | Snabbare |
| Kräver C-kompilator | Nej | Ja |
| Riktig native-kod | Nej | Ja |

För de flesta användare är det enklast och rekommenderat att köra `launcher.py` direkt (eller via `install.sh`) utan något byggsteg.

---

## License

MIT
