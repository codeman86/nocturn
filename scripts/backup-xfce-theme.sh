#!/usr/bin/env bash
# Save current XFCE GTK/icon/window-manager theme settings (and optional user theme files).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${HOME}/.local/share/nocturn-theme-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${BACKUP_ROOT}/${STAMP}"

usage() {
  echo "Usage: $0 [--with-files]"
  echo "  default: save xfconf theme settings to ${BACKUP_ROOT}/<timestamp>/"
  echo "  --with-files: also copy ~/.themes and ~/.icons entries for active themes"
  exit 1
}

WITH_FILES=0
if [[ "${1:-}" == "--with-files" ]]; then
  WITH_FILES=1
elif [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
elif [[ -n "${1:-}" ]]; then
  usage
fi

if ! command -v xfconf-query >/dev/null 2>&1; then
  echo "xfconf-query not found. This script is for XFCE." >&2
  exit 1
fi

mkdir -p "${BACKUP_DIR}"

read_xfconf() {
  local channel="$1" prop="$2"
  xfconf-query -c "$channel" -p "$prop" 2>/dev/null || echo ""
}

GTK_THEME="$(read_xfconf xsettings /Net/ThemeName)"
ICON_THEME="$(read_xfconf xsettings /Net/IconThemeName)"
CURSOR_THEME="$(read_xfconf xsettings /Gtk/CursorThemeName)"
WM_THEME="$(read_xfconf xfwm4 /general/theme)"
FONT_NAME="$(read_xfconf xsettings /Gtk/FontName)"

cat > "${BACKUP_DIR}/settings.env" <<EOF
# Nocturn theme backup — ${STAMP}
# Restore with: ./scripts/restore-xfce-theme.sh "${BACKUP_DIR}"
BACKUP_STAMP=${STAMP}
GTK_THEME=${GTK_THEME}
ICON_THEME=${ICON_THEME}
CURSOR_THEME=${CURSOR_THEME}
WM_THEME=${WM_THEME}
FONT_NAME=${FONT_NAME}
EOF

# Whisker Menu instances (plugin paths vary by panel layout).
WHISKER_FILE="${BACKUP_DIR}/whisker-menu-icons.txt"
: > "${WHISKER_FILE}"
while IFS= read -r prop; do
  [[ -n "$prop" ]] || continue
  if [[ "$(xfconf-query -c xfce4-panel -p "$prop" 2>/dev/null)" == "whiskermenu" ]]; then
    base="${prop%/plugin-name}"
    icon_prop="${base}/button-icon"
    icon_val="$(read_xfconf xfce4-panel "$icon_prop")"
    printf '%s=%s\n' "$icon_prop" "$icon_val" >> "${WHISKER_FILE}"
  fi
done < <(xfconf-query -c xfce4-panel -l 2>/dev/null | grep '/plugin-name$' || true)

if [[ "$WITH_FILES" -eq 1 ]]; then
  mkdir -p "${BACKUP_DIR}/themes" "${BACKUP_DIR}/icons"
  for name in "$GTK_THEME" "$WM_THEME"; do
    [[ -n "$name" && -d "${HOME}/.themes/${name}" ]] || continue
    cp -a "${HOME}/.themes/${name}" "${BACKUP_DIR}/themes/"
  done
  if [[ -n "$ICON_THEME" && -d "${HOME}/.icons/${ICON_THEME}" ]]; then
    cp -a "${HOME}/.icons/${ICON_THEME}" "${BACKUP_DIR}/icons/"
  fi
fi

ln -sfn "${BACKUP_DIR}" "${BACKUP_ROOT}/latest"

echo "Backup saved: ${BACKUP_DIR}"
echo ""
echo "Current settings:"
echo "  GTK theme:   ${GTK_THEME:-<unset>}"
echo "  Icon theme:  ${ICON_THEME:-<unset>}"
echo "  Cursor:      ${CURSOR_THEME:-<unset>}"
echo "  Window mgr:  ${WM_THEME:-<unset>}"
echo "  Font:        ${FONT_NAME:-<unset>}"
echo ""
echo "Restore later:"
echo "  ./scripts/restore-xfce-theme.sh latest"
echo ""
echo "Tip: log out/in after restore if panel icons look stale."
