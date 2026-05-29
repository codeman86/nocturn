#!/usr/bin/env bash
# Install Nocturn GTK theme, icon theme, and apply Xfce defaults.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
THEME_SRC="${ROOT}/themes/Nocturn"
ICON_SRC="${ROOT}/icons/Nocturn"
THEME_NAME="Nocturn"
ICON_NAME="Nocturn"
MENU_ICON="start-here"

usage() {
  echo "Usage: $0 [--system]"
  echo "  default: install to ~/.themes and ~/.icons"
  echo "  --system: install to /usr/share (requires root)"
  exit 1
}

SYSTEM=0
if [[ "${1:-}" == "--system" ]]; then
  SYSTEM=1
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "Re-run with sudo for system-wide install." >&2
    exit 1
  fi
elif [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
elif [[ -n "${1:-}" ]]; then
  usage
fi

if [[ "$SYSTEM" -eq 1 ]]; then
  THEME_TARGET="/usr/share/themes/${THEME_NAME}"
  ICON_TARGET="/usr/share/icons/${ICON_NAME}"
else
  THEME_TARGET="${HOME}/.themes/${THEME_NAME}"
  ICON_TARGET="${HOME}/.icons/${ICON_NAME}"
fi

if [[ ! -d "${THEME_SRC}" ]]; then
  echo "Theme source not found: ${THEME_SRC}" >&2
  exit 1
fi
if [[ ! -d "${ICON_SRC}" ]]; then
  echo "Icon source not found: ${ICON_SRC}" >&2
  exit 1
fi

install_tree() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "${dest}")"
  rm -rf "${dest}"
  cp -a "${src}" "${dest}"
}

install_tree "${THEME_SRC}" "${THEME_TARGET}"
install_tree "${ICON_SRC}" "${ICON_TARGET}"

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "${ICON_TARGET}" 2>/dev/null || true
fi

apply_xfce() {
  command -v xfconf-query >/dev/null 2>&1 || return 0

  xfconf-query -c xsettings -p /Net/ThemeName -s "${THEME_NAME}" 2>/dev/null || \
    xfconf-query -c xsettings -p /Net/ThemeName -n -t string -s "${THEME_NAME}" 2>/dev/null || true

  xfconf-query -c xsettings -p /Net/IconThemeName -s "${ICON_NAME}" 2>/dev/null || \
    xfconf-query -c xsettings -p /Net/IconThemeName -n -t string -s "${ICON_NAME}" 2>/dev/null || true

  xfconf-query -c xfwm4 -p /general/theme -s "${THEME_NAME}" 2>/dev/null || \
    xfconf-query -c xfwm4 -p /general/theme -n -t string -s "${THEME_NAME}" 2>/dev/null || true

  # Whisker Menu: set shelter icon on every whiskermenu plugin instance.
  while IFS= read -r prop; do
    [[ -n "$prop" ]] || continue
    if [[ "$(xfconf-query -c xfce4-panel -p "$prop" 2>/dev/null)" == "whiskermenu" ]]; then
      base="${prop%/plugin-name}"
      xfconf-query -c xfce4-panel -p "${base}/button-icon" -s "${MENU_ICON}" 2>/dev/null || \
        xfconf-query -c xfce4-panel -p "${base}/button-icon" -n -t string -s "${MENU_ICON}" 2>/dev/null || true
    fi
  done < <(xfconf-query -c xfce4-panel -l 2>/dev/null | grep '/plugin-name$' || true)
}

apply_xfce

echo "Installed ${THEME_NAME} -> ${THEME_TARGET}"
echo "Installed ${ICON_NAME} icons -> ${ICON_TARGET}"
echo ""
echo "Applied (when xfconf-query is available):"
echo "  GTK theme: ${THEME_NAME}"
echo "  Icon theme: ${ICON_NAME}"
echo "  Window manager theme: ${THEME_NAME}"
echo "  Whisker Menu icon: ${MENU_ICON}"
echo ""
echo "Log out and back in if panel icons do not refresh immediately."
