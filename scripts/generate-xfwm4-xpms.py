#!/usr/bin/env python3
"""Generate xfwm4 XPM assets for Nocturn-Dark theme."""

from pathlib import Path

THEME_XFWM = Path(__file__).resolve().parents[1] / "themes" / "Nocturn" / "xfwm4"

TITLE_H = 30
TITLE_W = 4


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.name}")


def solid_tile(name: str, w: int, h: int, color_sym: str) -> str:
    lines = [
        "/* XPM */",
        f'static char * {name}[] = {{',
        f'"{w} {h} 2 1",',
        '"  c None",',
        f'"@  c {color_sym}",',
    ]
    row = "@" * w
    lines.extend(f'"{row}",' for _ in range(h))
    lines.append("};")
    return "\n".join(lines) + "\n"


def window_button(name: str, glyph_rows: list[str], fg: str, hover_fg: str | None = None) -> str:
    size = len(glyph_rows)
    colors = ['"  c None",', f'". c {fg}",']
    if hover_fg:
        colors.append(f'"h c {hover_fg}",')
    lines = [
        "/* XPM */",
        f'static char * {name}[] = {{',
        f'"{size} {size} {len(colors)} 1",',
        *colors,
    ]
    for row in glyph_rows:
        lines.append(f'"{row}",')
    lines.append("};")
    return "\n".join(lines) + "\n"


# 12x12 window control glyphs (. = fg, space = transparent)
CLOSE = [
    "            ",
    "  ..    ..  ",
    "   ..  ..   ",
    "    ....    ",
    "     ..     ",
    "    ....    ",
    "   ..  ..   ",
    "  ..    ..  ",
    "            ",
    "            ",
    "            ",
    "            ",
]
HIDE = [
    "            ",
    "            ",
    "            ",
    "            ",
    "  ........  ",
    "  ........  ",
    "            ",
    "            ",
    "            ",
    "            ",
    "            ",
    "            ",
]
MAX = [
    "            ",
    "  ........  ",
    "  ........  ",
    "  ........  ",
    "  ........  ",
    "  ........  ",
    "  ........  ",
    "  ........  ",
    "            ",
    "            ",
    "            ",
    "            ",
]


def main() -> None:
    xfwm = THEME_XFWM
    print(f"Generating xfwm4 assets in {xfwm}")

    for i in range(1, 6):
        write(
            xfwm / f"title-{i}-active.xpm",
            solid_tile(f"title_{i}_active_xpm", TITLE_W, TITLE_H, "#252526 s active_color_1"),
        )
        write(
            xfwm / f"title-{i}-inactive.xpm",
            solid_tile(f"title_{i}_inactive_xpm", TITLE_W, TITLE_H, "#1e1e1e s inactive_color_1"),
        )

    for side, sym_a, sym_i in [
        ("left", "active_color_2", "inactive_color_2"),
        ("right", "active_color_2", "inactive_color_2"),
        ("bottom", "active_color_2", "inactive_color_2"),
    ]:
        write(xfwm / f"{side}-active.xpm", solid_tile(f"{side}_active_xpm", 4, 4, f"#1e1e1e s {sym_a}"))
        write(xfwm / f"{side}-inactive.xpm", solid_tile(f"{side}_inactive_xpm", 4, 4, f"#181818 s {sym_i}"))

    for corner, sym_a, sym_i in [
        ("top-left", "active_color_1", "inactive_color_1"),
        ("top-right", "active_color_1", "inactive_color_1"),
        ("bottom-left", "active_color_2", "inactive_color_2"),
        ("bottom-right", "active_color_2", "inactive_color_2"),
    ]:
        write(xfwm / f"{corner}-active.xpm", solid_tile(f"{corner.replace('-', '_')}_active_xpm", 4, 4, f"#252526 s {sym_a}"))
        write(xfwm / f"{corner}-inactive.xpm", solid_tile(f"{corner.replace('-', '_')}_inactive_xpm", 4, 4, f"#1e1e1e s {sym_i}"))

    fg = "#cccccc"
    close_hover = "#f48771"
    accent_hover = "#40916c"

    for btn, glyph in [("close", CLOSE), ("hide", HIDE), ("maximize", MAX)]:
        for state, color in [
            ("active", fg),
            ("inactive", "#858585"),
            ("prelight", accent_hover if btn != "close" else close_hover),
            ("pressed", "#52b788" if btn != "close" else close_hover),
        ]:
            rows = [r.replace(".", ".") for r in glyph]
            write(xfwm / f"{btn}-{state}.xpm", window_button(f"{btn}_{state}_xpm", rows, color))

    # Maximized variant (optional duplicate)
    write(xfwm / "maximize-active.xpm", window_button("maximize_active_xpm", MAX, fg))

    print("Done.")


if __name__ == "__main__":
    main()
