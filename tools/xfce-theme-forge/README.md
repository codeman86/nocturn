# XFCE Theme Forge

Generate complete XFCE/GTK themes from a JSON (or YAML) config — built from the **Nocturn** reference theme.

## What it generates

- GTK 3 / 4 CSS (recolored from base theme)
- xfwm4 window borders + `themerc` + XPM buttons
- Icon theme with shelter-style menu icon
- Pixmap SVG for Whisker Menu (`dist/pixmaps/YourTheme.svg`)
- Browser preview HTML

## Quick start

```bash
cd /path/to/nocturn

# 1. Create a config from a preset
python tools/xfce-theme-forge/theme-forge.py init MyTheme --preset cursor-blue

# 2. Edit colors in configs/MyTheme.json

# 3. Build
python tools/xfce-theme-forge/theme-forge.py build configs/MyTheme.json

# 4. Install on Linux (user)
python tools/xfce-theme-forge/theme-forge.py install configs/MyTheme.json
```

Rebuild the official Nocturn theme:

```bash
python tools/xfce-theme-forge/theme-forge.py build configs/nocturn.json
```

Output lands in `dist/Nocturn/` (does not overwrite `themes/Nocturn/`).

## Presets

```bash
python tools/xfce-theme-forge/theme-forge.py presets
```

| Preset | Description |
|--------|-------------|
| `nocturn` | Forest green (default) |
| `cursor-blue` | Cursor-like blue accent |
| `midnight-purple` | Purple accent |
| `ember` | Orange accent |

## Config options

```json
{
  "name": "MyTheme",
  "display_name": "My Theme",
  "comment": "Optional description",
  "output_dir": "dist",
  "base_theme": "Nocturn",
  "colors": { "accent_bright": "#40916c", ... },
  "options": {
    "square_corners": true,
    "whisker_menu": true,
    "generate_menu_icon": true,
    "menu_icon_ring": "#cccccc",
    "menu_icon_fill": "#40916c",
    "icon_theme_name": "MyTheme"
  }
}
```

## Menu icon on Archcraft

After install, copy pixmap to system path if needed:

```bash
sudo cp dist/pixmaps/MyTheme.svg /usr/share/pixmaps/
```

Then **Whisker Menu → Properties → Icon → Pixmaps → MyTheme.svg**

## Roadmap

- [ ] Web UI color picker + live preview
- [ ] Rounded corner mode tuning
- [ ] Export `.theme` zip for sharing
- [ ] Integrate backup/restore from main install scripts

## Requirements

- Python 3.10+
- Optional: `pyyaml` for YAML configs
