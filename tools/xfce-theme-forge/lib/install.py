"""Install generated themes to user or system paths."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .builder import _icon_output_root, _repo_root, _theme_output_root
from .config import ThemeConfig


def install_theme(config: ThemeConfig, system: bool = False, repo_root: Path | None = None) -> None:
    repo_root = repo_root or _repo_root()
    theme_src = _theme_output_root(config, repo_root)
    icon_src = _icon_output_root(config, repo_root)
    pixmap_src = repo_root / config.output_dir / "pixmaps" / f"{config.name}.svg"

    if not theme_src.is_dir():
        raise FileNotFoundError(f"Build the theme first: {theme_src}")

    if system:
        theme_dest = Path("/usr/share/themes") / config.name
        icon_dest = Path("/usr/share/icons") / config.icon_theme_name
        pixmap_dest = Path("/usr/share/pixmaps") / f"{config.name}.svg"
    else:
        theme_dest = Path.home() / ".themes" / config.name
        icon_dest = Path.home() / ".icons" / config.icon_theme_name
        pixmap_dest = Path.home() / ".local/share/pixmaps" / f"{config.name}.svg"

    _copy_tree(theme_src, theme_dest)
    if icon_src.is_dir():
        _copy_tree(icon_src, icon_dest)
        _run(["gtk-update-icon-cache", "-f", "-t", str(icon_dest)], optional=True)

    if pixmap_src.is_file():
        pixmap_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pixmap_src, pixmap_dest)
        print(f"Installed pixmap -> {pixmap_dest}")

    _apply_xfconf(config, system)
    _run(["xfce4-panel", "-r"], optional=True)


def _copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"Installed {src.name} -> {dest}")


def _run(cmd: list[str], optional: bool = False) -> None:
    try:
        subprocess.run(cmd, check=False)
    except FileNotFoundError:
        if not optional:
            print(f"Warning: command not found: {cmd[0]}")


def _apply_xfconf(config: ThemeConfig, system: bool) -> None:
    if system:
        print("System install complete. Set theme in Settings or xfconf-query.")
        return
    queries = [
        ("xsettings", "/Net/ThemeName", config.name),
        ("xsettings", "/Net/IconThemeName", config.icon_theme_name),
        ("xfwm4", "/general/theme", config.name),
    ]
    for channel, prop, value in queries:
        ok = subprocess.run(
            ["xfconf-query", "-c", channel, "-p", prop, "-s", value],
            check=False,
            capture_output=True,
        ).returncode == 0
        if not ok:
            subprocess.run(
                ["xfconf-query", "-c", channel, "-p", prop, "-n", "-t", "string", "-s", value],
                check=False,
            )
