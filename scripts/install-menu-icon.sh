#!/usr/bin/env bash
# Copy Nocturn menu icon into XFCE pixmaps folders (Whisker Menu → Icon → Pixmaps).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
PIXMAP_SRC="${ROOT}/icons/pixmaps/Nocturn.svg"

USER_PIXMAP_DIR="${HOME}/.local/share/pixmaps"
SYSTEM_PIXMAP_DIR="/usr/share/pixmaps"

INSTALL_USER=0
INSTALL_SYSTEM=0
APPLY_WHISKER=0

usage() {
  cat <<EOF
Usage: $0 [options]

Copy Nocturn.svg (and Nocturn.png when possible) into pixmaps so Whisker Menu
can pick it under Icon → Pixmaps.

Options:
  --user            Install to ~/.local/share/pixmaps (default if no target given)
  --system          Install to /usr/share/pixmaps (requires root; Archcraft often needs this)
  --apply-whisker   Set Whisker Menu button-icon to the installed file
  -h, --help        Show this help

Examples:
  sudo $0 --system
  $0 --apply-whisker
  sudo $0 --system && $0 --apply-whisker
EOF
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) INSTALL_USER=1 ;;
    --system) INSTALL_SYSTEM=1 ;;
    --apply-whisker) APPLY_WHISKER=1 ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown option: $1" >&2; usage 1 ;;
  esac
  shift
done

# Default: user pixmaps only
if [[ "$INSTALL_USER" -eq 0 && "$INSTALL_SYSTEM" -eq 0 ]]; then
  INSTALL_USER=1
fi

if [[ ! -f "${PIXMAP_SRC}" ]]; then
  echo "Pixmap source not found: ${PIXMAP_SRC}" >&2
  exit 1
fi

if [[ "$INSTALL_SYSTEM" -eq 1 && "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Re-run with sudo to install into ${SYSTEM_PIXMAP_DIR}" >&2
  exit 1
fi

install_pixmap_files() {
  local dest_dir="$1"
  mkdir -p "${dest_dir}"
  install -Dm644 "${PIXMAP_SRC}" "${dest_dir}/Nocturn.svg"
  echo "Installed ${dest_dir}/Nocturn.svg"

  local png="${dest_dir}/Nocturn.png"
  if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 48 -h 48 "${PIXMAP_SRC}" -o "${png}"
    echo "Installed ${png}"
  elif command -v magick >/dev/null 2>&1; then
    magick -background none "${PIXMAP_SRC}" -resize 48x48 "${png}"
    echo "Installed ${png}"
  elif command -v convert >/dev/null 2>&1; then
    convert -background none "${PIXMAP_SRC}" -resize 48x48 "${png}"
    echo "Installed ${png}"
  else
    echo "Tip: install rsvg-convert or imagemagick to also create Nocturn.png (often better on the panel)."
  fi
}

MENU_ICON=""

if [[ "$INSTALL_USER" -eq 1 ]]; then
  if [[ "${EUID:-$(id -u)}" -eq 0 && -n "${SUDO_USER:-}" ]]; then
    USER_PIXMAP_DIR="$(getent passwd "$SUDO_USER" | cut -d: -f6)/.local/share/pixmaps"
  fi
  install_pixmap_files "${USER_PIXMAP_DIR}"
  MENU_ICON="${USER_PIXMAP_DIR}/Nocturn.svg"
  if [[ -f "${USER_PIXMAP_DIR}/Nocturn.png" ]]; then
    MENU_ICON="${USER_PIXMAP_DIR}/Nocturn.png"
  fi
fi

if [[ "$INSTALL_SYSTEM" -eq 1 ]]; then
  install_pixmap_files "${SYSTEM_PIXMAP_DIR}"
  MENU_ICON="${SYSTEM_PIXMAP_DIR}/Nocturn.svg"
  if [[ -f "${SYSTEM_PIXMAP_DIR}/Nocturn.png" ]]; then
    MENU_ICON="${SYSTEM_PIXMAP_DIR}/Nocturn.png"
  fi
fi

if [[ "$APPLY_WHISKER" -eq 1 && -z "$MENU_ICON" ]]; then
  for candidate in \
    "${SYSTEM_PIXMAP_DIR}/Nocturn.png" \
    "${SYSTEM_PIXMAP_DIR}/Nocturn.svg" \
    "${HOME}/.local/share/pixmaps/Nocturn.png" \
    "${HOME}/.local/share/pixmaps/Nocturn.svg"; do
    if [[ -f "$candidate" ]]; then
      MENU_ICON="$candidate"
      break
    fi
  done
fi

apply_whisker_icon() {
  local icon_path="$1"
  command -v xfconf-query >/dev/null 2>&1 || return 0

  while IFS= read -r prop; do
    [[ -n "$prop" ]] || continue
    if [[ "$(xfconf-query -c xfce4-panel -p "$prop" 2>/dev/null)" == "whiskermenu" ]]; then
      base="${prop%/plugin-name}"
      xfconf-query -c xfce4-panel -p "${base}/button-icon" -s "${icon_path}" 2>/dev/null || \
        xfconf-query -c xfce4-panel -p "${base}/button-icon" -n -t string -s "${icon_path}" 2>/dev/null || true
    fi
  done < <(xfconf-query -c xfce4-panel -l 2>/dev/null | grep '/plugin-name$' || true)
}

if [[ "$APPLY_WHISKER" -eq 1 && -n "$MENU_ICON" ]]; then
  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    echo ""
    echo "Pixmap files are installed. Apply the menu icon as your user (not sudo):"
    echo "  cd ~/nocturn && ./scripts/install-menu-icon.sh --apply-whisker"
    echo "Or pick Pixmaps → Nocturn.png in Whisker Menu → Properties → Icon."
  else
    apply_whisker_icon "${MENU_ICON}"
    echo "Whisker Menu icon set to: ${MENU_ICON}"
    if xfce4-panel -r 2>/dev/null; then
      echo "Panel reloaded."
    else
      echo "Panel reload skipped — log out and back in, or run: xfce4-panel -r"
    fi
  fi
fi

echo ""
echo "Open Whisker Menu → Properties → Icon → Pixmaps and choose Nocturn.svg or Nocturn.png."
