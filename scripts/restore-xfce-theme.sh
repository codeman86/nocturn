#!/usr/bin/env bash
# Restore XFCE theme settings from backup-xfce-theme.sh output.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${HOME}/.local/share/nocturn-theme-backups"

usage() {
  echo "Usage: $0 [backup-dir|latest]"
  echo "  Restores GTK, icon, cursor, xfwm4, and Whisker Menu icon settings."
  exit 1
}

TARGET="${1:-latest}"
if [[ "$TARGET" == "latest" ]]; then
  TARGET="${BACKUP_ROOT}/latest"
fi
if [[ ! -d "$TARGET" ]]; then
  echo "Backup not found: ${TARGET}" >&2
  usage
fi

SETTINGS="${TARGET}/settings.env"
if [[ ! -f "$SETTINGS" ]]; then
  echo "Missing ${SETTINGS}" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$SETTINGS"

if ! command -v xfconf-query >/dev/null 2>&1; then
  echo "xfconf-query not found. This script is for XFCE." >&2
  exit 1
fi

set_xfconf() {
  local channel="$1" prop="$2" value="$3"
  [[ -n "$value" ]] || return 0
  xfconf-query -c "$channel" -p "$prop" -s "$value" 2>/dev/null || \
    xfconf-query -c "$channel" -p "$prop" -n -t string -s "$value" 2>/dev/null || true
}

set_xfconf xsettings /Net/ThemeName "${GTK_THEME:-}"
set_xfconf xsettings /Net/IconThemeName "${ICON_THEME:-}"
set_xfconf xsettings /Gtk/CursorThemeName "${CURSOR_THEME:-}"
set_xfconf xfwm4 /general/theme "${WM_THEME:-}"
set_xfconf xsettings /Gtk/FontName "${FONT_NAME:-}"

WHISKER_FILE="${TARGET}/whisker-menu-icons.txt"
if [[ -f "$WHISKER_FILE" ]]; then
  while IFS='=' read -r prop value; do
    [[ -n "$prop" ]] || continue
    set_xfconf xfce4-panel "$prop" "$value"
  done < "$WHISKER_FILE"
fi

if [[ -d "${TARGET}/themes" ]]; then
  mkdir -p "${HOME}/.themes"
  cp -a "${TARGET}/themes/"* "${HOME}/.themes/" 2>/dev/null || true
fi
if [[ -d "${TARGET}/icons" ]]; then
  mkdir -p "${HOME}/.icons"
  cp -a "${TARGET}/icons/"* "${HOME}/.icons/" 2>/dev/null || true
fi

echo "Restored from: ${TARGET}"
echo "  GTK theme:   ${GTK_THEME:-<unset>}"
echo "  Icon theme:  ${ICON_THEME:-<unset>}"
echo "  Window mgr:  ${WM_THEME:-<unset>}"
echo ""
echo "Log out and back in if the panel or windows do not update."
