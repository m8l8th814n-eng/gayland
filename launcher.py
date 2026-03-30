#!/usr/bin/env python3
"""
wlauncher — dmenu/dmenu_run-ersättning för Wayland/Hyprland
Fungerar med wlroots-baserade compositorer via gtk-layer-shell
"""

import gi
gi.require_version('Gtk', '3.0')
try:
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import GtkLayerShell
    HAS_LAYER_SHELL = True
except (ValueError, ImportError):
    HAS_LAYER_SHELL = False

from gi.repository import Gtk, Gdk, GLib, Pango
import os
import subprocess
import sys
import configparser
import random

# ─── Standardkonfiguration ───────────────────────────────────────────────────

CONFIG_PATH = os.path.expanduser('~/.config/wlauncher/config.ini')

DEFAULT_CONFIG_TEXT = """\
[colors]
# Bakgrundsfärg: hexkod (#rrggbb) eller "random"
background = #000000
# Förgrundsfärg: hexkod (#rrggbb), "random" eller "gay" (regnbåge som blinkar)
foreground = #ffffff

[font]
# Typsnittsnamn
name = monospace
# Storlek i punkter
size = 14

[window]
# Position: top eller bottom
position = bottom
# Höjd i pixlar
height = 32
# Max antal sökresultat att visa
max_results = 12
"""

# ─── Färgpalett för gay/random ────────────────────────────────────────────────

GAY_COLORS = [
    '#FF0018', '#FF4500', '#FFA52C', '#FFD700', '#FFFF41',
    '#ADFF2F', '#00FF00', '#00FA9A', '#00FFFF', '#00BFFF',
    '#0000F9', '#7B68EE', '#9400D3', '#FF00FF', '#FF69B4',
    '#FF1493', '#FF6347', '#20B2AA', '#86007D', '#FF8C00',
]

RANDOM_COLORS = [
    '#FF5555', '#50FA7B', '#F1FA8C', '#BD93F9', '#FFB86C',
    '#FF79C6', '#8BE9FD', '#6272A4', '#FF6E6E', '#69FF94',
    '#FFFFA5', '#D6ACFF', '#FFD29A', '#FF92DF', '#A4FFFF',
]


# ─── Hjälpfunktioner ─────────────────────────────────────────────────────────

def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read_string(DEFAULT_CONFIG_TEXT)

    config_dir = os.path.dirname(CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            f.write(DEFAULT_CONFIG_TEXT)

    config.read(CONFIG_PATH)
    return config


def get_executables() -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for d in os.environ.get('PATH', '').split(':'):
        try:
            for name in sorted(os.listdir(d)):
                if name in seen:
                    continue
                full = os.path.join(d, name)
                if os.path.isfile(full) and os.access(full, os.X_OK):
                    seen.add(name)
                    result.append(name)
        except (PermissionError, FileNotFoundError, NotADirectoryError):
            pass
    return sorted(result, key=str.lower)


def make_rainbow_markup(text: str, offset: int = 0) -> str:
    """Pango-markup där varje tecken får en regnbågsfärg (offset styr fasen)."""
    parts = []
    for i, ch in enumerate(text):
        color = GAY_COLORS[(i + offset) % len(GAY_COLORS)]
        escaped = GLib.markup_escape_text(ch)
        parts.append(f'<span foreground="{color}">{escaped}</span>')
    return ''.join(parts)


def resolve_color(value: str, palette: list[str]) -> str:
    v = value.strip().lower()
    if v == 'random':
        return random.choice(palette)
    return value.strip()


# ─── Huvud-widget ─────────────────────────────────────────────────────────────

class Launcher(Gtk.Window):

    def __init__(self, config: configparser.ConfigParser, executables: list[str]):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.config = config
        self.all_executables = executables
        self.filtered: list[str] = []
        self.selected_index = 0
        self.gay_mode = False
        self.gay_offset = 0

        bg_raw = config.get('colors', 'background', fallback='#000000')
        fg_raw = config.get('colors', 'foreground', fallback='#ffffff')

        self.bg = resolve_color(bg_raw, RANDOM_COLORS)
        if fg_raw.strip().lower() == 'gay':
            self.gay_mode = True
            self.fg = GAY_COLORS[0]
        else:
            self.fg = resolve_color(fg_raw, RANDOM_COLORS)

        self._setup_layer_shell()
        self._apply_css()
        self._build_ui()
        self._connect_signals()
        self._update_matches('')

        if self.gay_mode:
            GLib.timeout_add(70, self._tick_gay)

    # ── Fönsterinställningar ──────────────────────────────────────────────────

    def _setup_layer_shell(self):
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_app_paintable(True)

        height = self.config.getint('window', 'height', fallback=32)
        position = self.config.get('window', 'position', fallback='bottom').strip().lower()

        if HAS_LAYER_SHELL:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
            # exclusive_zone = -1 → täck inte waybar utan lägg sig ovanpå/under
            GtkLayerShell.set_exclusive_zone(self, height)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT,   True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT,  True)
            if position == 'top':
                GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP,    True)
                GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, False)
            else:
                GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
                GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP,    False)
            GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        else:
            # Fallback utan layer-shell (X11 / test)
            self.set_keep_above(True)
            self.set_skip_taskbar_hint(True)
            screen = Gdk.Screen.get_default()
            sw = screen.get_width() if screen else 1920
            sh = screen.get_height() if screen else 1080
            if position == 'top':
                self.move(0, 0)
            else:
                self.move(0, sh - height)
            self.set_default_size(sw, height)

    # ── CSS ──────────────────────────────────────────────────────────────────

    def _build_css(self, fg: str) -> str:
        bg = self.bg
        font = self.config.get('font', 'name', fallback='monospace').strip()
        size = self.config.getint('font', 'size', fallback=14)
        return f"""
        window, .launcher-root {{
            background-color: {bg};
            border: none;
            padding: 0;
            margin: 0;
        }}
        .launcher-root {{
            padding: 0 6px;
        }}
        .prompt {{
            color: {fg};
            font-family: "{font}";
            font-size: {size}pt;
            font-weight: bold;
            padding: 0 4px 0 0;
        }}
        .launcher-entry {{
            background-color: {bg};
            color: {fg};
            caret-color: {fg};
            border: none;
            box-shadow: none;
            outline: none;
            font-family: "{font}";
            font-size: {size}pt;
            min-width: 220px;
            padding: 0 8px 0 0;
        }}
        .launcher-entry:focus {{
            border: none;
            box-shadow: none;
            outline: none;
        }}
        .divider {{
            color: {fg};
            font-family: "{font}";
            font-size: {size}pt;
            opacity: 0.4;
            padding: 0 6px;
        }}
        .result {{
            color: {fg};
            font-family: "{font}";
            font-size: {size}pt;
            padding: 0 8px;
        }}
        .result-active {{
            background-color: {fg};
            color: {bg};
            font-family: "{font}";
            font-size: {size}pt;
            padding: 0 8px;
            border-radius: 2px;
        }}
        """

    def _apply_css(self, fg: str | None = None):
        if fg is None:
            fg = self.fg
        if not hasattr(self, '_css_provider'):
            self._css_provider = Gtk.CssProvider()
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                self._css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
        self._css_provider.load_from_data(self._build_css(fg).encode())

    # ── UI-byggnad ────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=0,
        )
        self.root_box.get_style_context().add_class('launcher-root')
        self.add(self.root_box)

        self.prompt_label = Gtk.Label(label='run:')
        self.prompt_label.get_style_context().add_class('prompt')
        self.root_box.pack_start(self.prompt_label, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.get_style_context().add_class('launcher-entry')
        self.entry.set_has_frame(False)
        self.root_box.pack_start(self.entry, False, False, 0)

        div = Gtk.Label(label='│')
        div.get_style_context().add_class('divider')
        self.root_box.pack_start(div, False, False, 0)

        self.results_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=0,
        )
        self.root_box.pack_start(self.results_box, True, True, 0)

        self._result_labels: list[Gtk.Label] = []

    # ── Signaler ─────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.entry.connect('changed', lambda w: self._update_matches(w.get_text()))
        self.entry.connect('key-press-event', self._on_key_press)
        self.connect('key-press-event', self._on_key_press)
        self.connect('delete-event', lambda *_: Gtk.main_quit())

    def _on_key_press(self, _widget, event) -> bool:
        k = event.keyval

        if k == Gdk.KEY_Escape:
            Gtk.main_quit()
            return True

        if k in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._launch_selected()
            return True

        if k == Gdk.KEY_Tab:
            # Tab → fyll in valt alternativ i inmatningsfältet
            if self.filtered:
                name = self.filtered[self.selected_index]
                self.entry.set_text(name)
                self.entry.set_position(len(name))
            return True

        if k in (Gdk.KEY_Right, Gdk.KEY_Down):
            self._move_selection(+1)
            return True

        if k == Gdk.KEY_Up:
            self._move_selection(-1)
            return True

        if k == Gdk.KEY_Left:
            # Gå bakåt i listan bara om markören är i början av fältet
            if self.entry.get_position() == 0:
                self._move_selection(-1)
                return True

        return False

    # ── Matchning & urval ─────────────────────────────────────────────────────

    def _update_matches(self, text: str):
        # Ta bort gamla labels
        for child in self.results_box.get_children():
            self.results_box.remove(child)
        self._result_labels = []

        query = text.strip().lower()
        max_r = self.config.getint('window', 'max_results', fallback=12)

        if query:
            starts = [e for e in self.all_executables if e.lower().startswith(query)]
            contains = [e for e in self.all_executables
                        if query in e.lower() and not e.lower().startswith(query)]
            matches = (starts + contains)[:max_r]
        else:
            matches = self.all_executables[:max_r]

        self.filtered = matches
        if self.selected_index >= len(matches):
            self.selected_index = 0

        for i, name in enumerate(matches):
            lbl = Gtk.Label()
            lbl.set_use_markup(True)
            if self.gay_mode:
                lbl.set_markup(make_rainbow_markup(name, self.gay_offset + i * 3))
            else:
                lbl.set_text(name)

            ctx = lbl.get_style_context()
            if i == self.selected_index:
                ctx.add_class('result-active')
            else:
                ctx.add_class('result')

            self.results_box.pack_start(lbl, False, False, 0)
            self._result_labels.append(lbl)

        self.results_box.show_all()

    def _move_selection(self, delta: int):
        if not self.filtered:
            return
        self.selected_index = (self.selected_index + delta) % len(self.filtered)
        self._refresh_selection()

    def _refresh_selection(self):
        for i, lbl in enumerate(self._result_labels):
            ctx = lbl.get_style_context()
            if i == self.selected_index:
                ctx.remove_class('result')
                ctx.add_class('result-active')
            else:
                ctx.remove_class('result-active')
                ctx.add_class('result')
            if self.gay_mode:
                lbl.set_markup(
                    make_rainbow_markup(self.filtered[i], self.gay_offset + i * 3)
                )

    # ── Gay-animation ─────────────────────────────────────────────────────────

    def _tick_gay(self) -> bool:
        self.gay_offset = (self.gay_offset + 1) % len(GAY_COLORS)
        color = GAY_COLORS[self.gay_offset]
        self._apply_css(color)

        # Uppdatera labels med skiftad offset
        for i, lbl in enumerate(self._result_labels):
            lbl.set_markup(
                make_rainbow_markup(self.filtered[i], self.gay_offset + i * 3)
            )

        return True  # Fortsätt timer

    # ── Starta program ────────────────────────────────────────────────────────

    def _launch_selected(self):
        text = self.entry.get_text().strip()

        if self.filtered and self.selected_index < len(self.filtered):
            cmd = self.filtered[self.selected_index]
        elif text:
            cmd = text
        else:
            return

        try:
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
                start_new_session=True,
            )
        except Exception:
            pass

        Gtk.main_quit()


# ─── Startpunkt ───────────────────────────────────────────────────────────────

def main():
    config = load_config()
    executables = get_executables()

    win = Launcher(config, executables)
    win.show_all()
    win.present()
    win.entry.grab_focus()

    Gtk.main()


if __name__ == '__main__':
    main()
