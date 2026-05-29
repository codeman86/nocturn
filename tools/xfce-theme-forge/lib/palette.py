"""Reference palette and recolor helpers for XFCE Theme Forge."""

from __future__ import annotations

REFERENCE_COLORS: dict[str, str] = {
    "bg": "#181818",
    "bg_alt": "#1e1e1e",
    "surface": "#252526",
    "surface_alt": "#2d2d2d",
    "border": "#3c3c3c",
    "border_subtle": "#2b2b2b",
    "fg": "#cccccc",
    "fg_dim": "#858585",
    "fg_bright": "#e8e8e8",
    "accent": "#2d6a4f",
    "accent_bright": "#40916c",
    "accent_dim": "#1b4332",
    "accent_glow": "#52b788",
    "selection": "#264f3f",
    "error": "#f48771",
    "warning": "#cca700",
    "success": "#4ade80",
}

PRESETS: dict[str, dict[str, str]] = {
    "nocturn": dict(REFERENCE_COLORS),
    "cursor-blue": {
        **REFERENCE_COLORS,
        "accent": "#0078d4",
        "accent_bright": "#3794ff",
        "accent_dim": "#005a9e",
        "accent_glow": "#4dabf7",
        "selection": "#264f78",
    },
    "midnight-purple": {
        **REFERENCE_COLORS,
        "accent": "#5b21b6",
        "accent_bright": "#7c3aed",
        "accent_dim": "#4c1d95",
        "accent_glow": "#a78bfa",
        "selection": "#3b2667",
    },
    "ember": {
        **REFERENCE_COLORS,
        "accent": "#9a3412",
        "accent_bright": "#ea580c",
        "accent_dim": "#7c2d12",
        "accent_glow": "#fb923c",
        "selection": "#5c2d12",
    },
}


def normalize_hex(value: str) -> str:
    value = value.strip().lower()
    if not value.startswith("#"):
        value = f"#{value}"
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    return value


def recolor_text(text: str, source: dict[str, str], target: dict[str, str]) -> str:
    merged = {**source, **target}
    for key, old in source.items():
        new = normalize_hex(merged.get(key, old))
        old_norm = normalize_hex(old)
        text = text.replace(old_norm, new)
        text = text.replace(old_norm.upper(), new)
    return text


def merge_colors(base: dict[str, str], overrides: dict[str, str] | None) -> dict[str, str]:
    result = {k: normalize_hex(v) for k, v in base.items()}
    if overrides:
        for key, value in overrides.items():
            if key in result:
                result[key] = normalize_hex(value)
    return result
