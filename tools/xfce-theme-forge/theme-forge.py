#!/usr/bin/env python3
"""
XFCE Theme Forge — generate GTK/XFCE themes from a simple config file.

Usage:
  python theme-forge.py init MyTheme [--preset nocturn]
  python theme-forge.py build configs/MyTheme.json
  python theme-forge.py install configs/MyTheme.json [--system]
  python theme-forge.py presets
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.builder import build_preview, build_theme  # noqa: E402
from lib.config import load_config, new_config, save_config  # noqa: E402
from lib.install import install_theme  # noqa: E402
from lib.palette import PRESETS  # noqa: E402

REPO_ROOT = ROOT.parents[1]
CONFIGS = REPO_ROOT / "configs"


def cmd_init(args: argparse.Namespace) -> int:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    path = Path(args.config) if args.config else CONFIGS / f"{args.name}.json"
    if path.exists() and not args.force:
        print(f"Config already exists: {path}\nUse --force to overwrite.")
        return 1
    config = new_config(args.name, preset=args.preset)
    save_config(path, config)
    print(f"Created config: {path}")
    print(f"Next: python {Path(__file__).name} build {path}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config))
    out = build_theme(config, REPO_ROOT)
    preview = build_preview(config, REPO_ROOT)
    print(f"Built theme: {out}")
    print(f"Preview:     {preview}")
    print(f"Icons:       {REPO_ROOT / config.output_dir / 'icons' / config.icon_theme_name}")
    print(f"Pixmap:      {REPO_ROOT / config.output_dir / 'pixmaps' / (config.name + '.svg')}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config))
    install_theme(config, system=args.system, repo_root=REPO_ROOT)
    print("Install finished.")
    if config.options.generate_menu_icon:
        print(f"Menu icon: set Whisker Menu → Pixmaps → {config.name}.svg")
    return 0


def cmd_presets(_: argparse.Namespace) -> int:
    print("Available presets:\n")
    for name, colors in PRESETS.items():
        print(f"  {name}")
        print(f"    accent: {colors['accent_bright']}  bg: {colors['bg']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="theme-forge",
        description="Generate XFCE/GTK themes from a JSON or YAML config.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new theme config")
    p_init.add_argument("name", help="Theme name (e.g. MyTheme)")
    p_init.add_argument("--preset", default="nocturn", choices=sorted(PRESETS))
    p_init.add_argument("--config", help="Config output path")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_build = sub.add_parser("build", help="Build theme from config")
    p_build.add_argument("config", help="Path to .json or .yaml config")
    p_build.set_defaults(func=cmd_build)

    p_install = sub.add_parser("install", help="Install built theme (build first)")
    p_install.add_argument("config", help="Path to config used for build")
    p_install.add_argument("--system", action="store_true")
    p_install.set_defaults(func=cmd_install)

    p_presets = sub.add_parser("presets", help="List color presets")
    p_presets.set_defaults(func=cmd_presets)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
