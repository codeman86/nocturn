# Nocturn

XFCE/GTK theme and icon set for **Nocturn Linux** — a Cursor-inspired dark desktop with forest green accents.

## Quick install (Arch / ArchCraft / any Xfce)

**Back up first** (recommended):

```bash
git clone https://github.com/codeman86/nocturn.git
cd nocturn
chmod +x scripts/backup-xfce-theme.sh scripts/install-nocturn-theme.sh scripts/install-menu-icon.sh
./scripts/backup-xfce-theme.sh
./scripts/install-nocturn-theme.sh
```

If the menu icon does not appear under **Whisker Menu → Pixmaps** (common on Archcraft):

```bash
sudo ./scripts/install-menu-icon.sh --system --apply-whisker
```

To undo and return to your previous look:

```bash
./scripts/restore-xfce-theme.sh latest
```

Add `--with-files` to the backup script if your themes live under `~/.themes` or `~/.icons` (copies those folders too). ArchCraft defaults often come from `/usr/share/themes` — the backup still saves the **names** of your active themes so restore puts those back.

## What's included

- **Nocturn** GTK + xfwm4 theme (`themes/Nocturn/`)
- **Nocturn** icon theme with shelter-style menu icon (`icons/Nocturn/`)
- Install, backup, and restore scripts for Xfce

## Repository layout

```
themes/Nocturn/     GTK / XFCE window theme
icons/Nocturn/      Menu icons (start-here, nocturn-menu)
scripts/            install, backup, restore
docs/PALETTE.md     Design colors
```

## Nocturn Linux website

Preview the project site locally:

```bash
cd website
python -m http.server 8080
# http://127.0.0.1:8080
```

See [website/README.md](website/README.md).

## XFCE Theme Forge

Generate new themes from a config file or **local web UI** (`theme-forge.py serve`):

```bash
python tools/xfce-theme-forge/theme-forge.py serve
# open http://127.0.0.1:8765
```

See [tools/xfce-theme-forge/README.md](tools/xfce-theme-forge/README.md).

## Preview without Linux

Open `themes/Nocturn/preview.html` in a browser on Windows or macOS.

## License

MIT
