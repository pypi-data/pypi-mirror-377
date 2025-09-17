from __future__ import annotations
import re
from typing import Iterable, Dict, Any, Optional


# --- tokens (extend as needed) ---
TOKENS = {
    "space": {
        "0": "0",
        "1": ".25rem",  "2": ".5rem",   "3": ".75rem",  "4": "1rem",
        "5": "1.25rem", "6": "1.5rem",  "7": "1.75rem", "8": "2rem",
        "9": "2.25rem", "10": "2.5rem", "11": "2.75rem","12": "3rem",
        "14": "3.5rem", "16": "4rem",   "20": "5rem",   "24": "6rem",
        "28": "7rem",   "32": "8rem"
    },
    "radius": {
        "none": "0", "sm": "8px", "md": "12px", "lg": "16px",
        "xl": "20px", "2xl": "24px", "3xl": "32px", "full": "9999px"
    },
    "shadow": {
        "none": "none",
        "sm":   "0 1px 3px rgba(0,0,0,.08)",
        "md":   "0 2px 6px rgba(0,0,0,.10)",
        "lg":   "0 6px 18px rgba(0,0,0,.12)",
        "xl":   "0 12px 32px rgba(0,0,0,.14)",
        "2xl":  "0 20px 56px rgba(0,0,0,.16)",
        "3xl":  "0 32px 80px rgba(0,0,0,.18)",
        "inner":"inset 0 2px 6px rgba(0,0,0,.12)"
    },
    "border_width": { "0": "0", "DEFAULT": "1px", "2": "2px", "4": "4px", "8": "8px" },
    "border_color": {
        "subtle": "rgba(15,23,42,.06)",
        "transparent": "transparent",
        "black": "rgba(0,0,0,1)",
        "white": "rgba(255,255,255,1)",
        "slate-200": "rgb(226,232,240)",
        "slate-300": "rgb(203,213,225)",
        "slate-400": "rgb(148,163,184)",
        "blue-500": "rgb(59,130,246)",
        "red-500": "rgb(239,68,68)",
        "green-500": "rgb(34,197,94)"
    }
}

FONT_SIZES = {
    "xs": "0.75rem", "sm": "0.875rem", "base": "1rem",
    "lg": "1.125rem", "xl": "1.25rem", "2xl": "1.5rem",
    "3xl": "1.875rem", "4xl": "2.25rem"
}

# Built-in palettes for -100..-900 (no :root vars needed)
PALETTES = {
    "red": {
        "50": "#fef2f2", "100": "#fee2e2", "200": "#fecaca", "300": "#fca5a5",
        "400": "#f87171", "500": "#ef4444", "600": "#dc2626", "700": "#b91c1c",
        "800": "#991b1b", "900": "#7f1d1d",
    },
    "blue": {
        "50": "#eff6ff", "100": "#dbeafe", "200": "#bfdbfe", "300": "#93c5fd",
        "400": "#60a5fa", "500": "#3b82f6", "600": "#2563eb", "700": "#1d4ed8",
        "800": "#1e40af", "900": "#1e3a8a",
    },
    "slate": {
        "50": "#f8fafc", "100": "#f1f5f9", "200": "#e2e8f0", "300": "#cbd5e1",
        "400": "#94a3b8", "500": "#64748b", "600": "#475569", "700": "#334155",
        "800": "#1f2937", "900": "#0f172a",
    },
    "green": {
        "50": "#f0fdf4", "100": "#dcfce7", "200": "#bbf7d0", "300": "#86efac",
        "400": "#4ade80", "500": "#22c55e", "600": "#16a34a", "700": "#15803d",
        "800": "#166534", "900": "#14532d",
    },
}

# --- responsive breakpoints ---
BPS = {
    "sm": "(min-width: 640px)",
    "md": "(min-width: 768px)",
    "lg": "(min-width: 1024px)",
}


_THEME_REGISTRY: Dict[str, Dict[str, Any]] = {}
_ACTIVE_THEME: Optional[str] = None

def register_theme(name: str, *, vars: Optional[dict] = None, **palettes: dict) -> None:
    """
    Register a theme with:
    - vars:     single-value tokens → emitted as --<key>: <value>
    - palettes: any number of color scales (e.g. brand, accent, warning ...)
                each is a dict like {"50":"...", "100":"...", ..., "900":"..."}
    Example:
        register_theme("light",
            vars={"bg-surface":"#fff", "text-body":"#0f172a"},
            brand={...},
            accent={...}  # arbitrary group name supported
        )
    """
    _THEME_REGISTRY[name] = {
        "vars": dict(vars or {}),
        "palettes": {k: dict(v) for k, v in palettes.items()},
    }

def set_active_theme(name: str) -> None:
    global _ACTIVE_THEME
    if name not in _THEME_REGISTRY:
        raise ValueError(f"set_active_theme: unknown theme '{name}'")
    _ACTIVE_THEME = name

def compile_theme_css() -> str:
    """
    Emit CSS vars for ALL registered themes, scoped under .theme-<name>.
    Does NOT touch :root.
    """
    blocks: list[str] = []
    for name, spec in _THEME_REGISTRY.items():
        lines: list[str] = []
        # single-value vars
        for k, v in spec.get("vars", {}).items():
            lines.append(f"--{k}: {v};")
        # palettes (brand/accent/warning/etc.)
        for group, palette in spec.get("palettes", {}).items():
            for step, color in palette.items():
                lines.append(f"--{group}-{step}: {color};")
        if lines:
            blocks.append(f".theme-{name}{{{''.join(lines)}}}")
    return "\n".join(blocks)


_used: set[str] = set()


def register_dzn_classes(classes: str | Iterable[str]) -> None:
    if isinstance(classes, str):
        _used.update(c for c in classes.split() if c)
    else:
        _used.update(classes)


# --- selector escaping for arbitrary utilities ---
def css_escape_class(cls: str) -> str:
    # Escape any char not [a-zA-Z0-9_-] so the selector matches the literal class in HTML
    return re.sub(r'([^a-zA-Z0-9_-])', r'\\\1', cls)


# --- emit helpers ---
def rule(selector: str, body: str) -> str:
    return f".{selector}{{{body}}}"


def emit_base(name: str) -> str | None:
    match name:

        case "object-cover":  return rule(name, "object-fit:cover")
        case "object-contain":return rule(name, "object-fit:contain")
        case "object-center": return rule(name, "object-position:center")
        case "w-full":        return rule(name, "width:100%")
        case "h-full":        return rule(name, "height:100%")

        # layout
        case "flex":            return rule(name, "display:flex")
        case "flex-col":        return rule(name, "flex-direction:column")
        case "items-center":    return rule(name, "align-items:center")
        case "justify-center":  return rule(name, "justify-content:center")
        case "text-center":     return rule(name, "text-align:center")

        case "items-start":   return rule(name, "align-items:flex-start")
        case "items-end":     return rule(name, "align-items:flex-end")
        case "justify-start": return rule(name, "justify-content:flex-start")
        case "justify-end":   return rule(name, "justify-content:flex-end")

        case "self-center": return rule(name, "align-self:center")
        case "self-start":  return rule(name, "align-self:flex-start")
        case "self-end":    return rule(name, "align-self:flex-end")

        # --- semantic aliases (themeable via CSS vars with fallbacks) ---
        case "bg-surface":   return rule(name, "background:var(--bg-surface, #ffffff)")
        case "bg-elevated":  return rule(name, "background:var(--bg-elevated, #ffffff)")
        case "bg-muted":     return rule(name, "background:var(--bg-muted, #f8fafc)")
        case "text-body":    return rule(name, "color:var(--text-body, #0f172a)")
        case "text-muted":   return rule(name, "color:var(--text-muted, #475569)")
        case "text-inverse": return rule(name, "color:var(--text-inverse, #ffffff)")
        case "border-subtle": return rule(name, f"border-color:var(--border-subtle, {TOKENS['border_color']['subtle']})")

        case "bg-cover":     return rule(name, "background-size:cover")
        case "bg-contain":   return rule(name, "background-size:contain")
        case "bg-center":    return rule(name, "background-position:center")
        case "bg-top":       return rule(name, "background-position:top")
        case "bg-bottom":    return rule(name, "background-position:bottom")
        case "bg-no-repeat": return rule(name, "background-repeat:no-repeat")
        case "bg-repeat":    return rule(name, "background-repeat:repeat")


        # border (longhand for predictable overrides)
        case "border":
            return rule(
                name,
                f"border-style:solid;"
                f"border-width:{TOKENS['border_width']['DEFAULT']};"
                f"border-color:{TOKENS['border_color']['subtle']}"
            )

        # quick border colors (keep, but don't re-define border-subtle here)
        case "border-transparent":  return rule(name, f"border-color:{TOKENS['border_color']['transparent']}")
        case "border-black":        return rule(name, f"border-color:{TOKENS['border_color']['black']}")
        case "border-white":        return rule(name, f"border-color:{TOKENS['border_color']['white']}")

        # radius
        case "rounded":         return rule(name, "border-radius:12px")
        case "rounded-none":    return rule(name, "border-radius:0")

        # shadows
        case "shadow-none":     return rule(name, f"box-shadow:{TOKENS['shadow']['none']}")
        case "shadow-sm":       return rule(name, f"box-shadow:{TOKENS['shadow']['sm']}")
        case "shadow":          return rule(name, f"box-shadow:{TOKENS['shadow']['md']}")
        case "shadow-md":       return rule(name, f"box-shadow:{TOKENS['shadow']['md']}")
        case "shadow-lg":       return rule(name, f"box-shadow:{TOKENS['shadow']['lg']}")
        case "shadow-xl":       return rule(name, f"box-shadow:{TOKENS['shadow']['xl']}")
        case "shadow-2xl":      return rule(name, f"box-shadow:{TOKENS['shadow']['2xl']}")
        case "shadow-3xl":      return rule(name, f"box-shadow:{TOKENS['shadow']['3xl']}")
        case "shadow-inner":    return rule(name, f"box-shadow:{TOKENS['shadow']['inner']}")

        # visibility
        case "hidden":       return rule(name, "display:none!important")
        case "block":        return rule(name, "display:block")
        case "inline-block": return rule(name, "display:inline-block")
        case "invisible":    return rule(name, "visibility:hidden")
        case "visible":      return rule(name, "visibility:visible")

        # positioning
        case "fixed":    return rule(name, "position:fixed")
        case "absolute": return rule(name, "position:absolute")
        case "relative": return rule(name, "position:relative")
        case "sticky":   return rule(name, "position:sticky")   # <-- ADD THIS
        case "top-0":    return rule(name, "top:0")
        case "right-0":  return rule(name, "right:0")
        case "bottom-0": return rule(name, "bottom:0")
        case "left-0":   return rule(name, "left:0")
        case "inset-0":  return rule(name, "top:0;right:0;bottom:0;left:0")

        case "flex-1":   return rule(name, "flex:1 1 0%")
        case "grow":     return rule(name, "flex-grow:1")
        case "shrink-0": return rule(name, "flex-shrink:0")

        case "grid": return rule(name, "display:grid")

        case "border-solid":  return rule(name, "border-style:solid")
        case "border-dashed": return rule(name, "border-style:dashed")
        case "border-dotted": return rule(name, "border-style:dotted")

        case "aspect-square": return rule(name, "aspect-ratio:1/1")

        # auto margins (centering helpers)
        case "mx-auto": return rule(name, "margin-left:auto;margin-right:auto")
        case "ml-auto": return rule(name, "margin-left:auto")
        case "mr-auto": return rule(name, "margin-right:auto")
        case "ms-auto": return rule(name, "margin-inline-start:auto")
        case "me-auto": return rule(name, "margin-inline-end:auto")

        # overflow helpers
        case "overflow-hidden":   return rule(name, "overflow:hidden")
        case "overflow-auto":     return rule(name, "overflow:auto")
        case "overflow-y-auto":   return rule(name, "overflow-y:auto")
        case "overflow-x-hidden": return rule(name, "overflow-x:hidden")
        case "overflow-y-hidden": return rule(name, "overflow-y:hidden")

        # overscroll-behavior
        case "overscroll-auto":    return rule(name, "overscroll-behavior:auto")
        case "overscroll-contain": return rule(name, "overscroll-behavior:contain")
        case "overscroll-none":    return rule(name, "overscroll-behavior:none")

        # optional: keep layout from shifting when scrollbar appears
        case "scrollbar-stable":   return rule(name, "scrollbar-gutter:stable")

        # text decoration (links etc.)
        case "no-underline":      return rule(name, "text-decoration:none")
        case "underline":         return rule(name, "text-decoration:underline")
        case "line-through":      return rule(name, "text-decoration:line-through")
        case "decoration-solid":  return rule(name, "text-decoration-style:solid")
        case "decoration-dashed": return rule(name, "text-decoration-style:dashed")
        case "decoration-dotted": return rule(name, "text-decoration-style:dotted")

        case "whitespace-nowrap": return rule(name, "white-space:nowrap")

    return None



def emit_scale(name: str) -> str | None:

    # font sizes
    if m := re.fullmatch(r"text-(xs|sm|base|lg|xl|2xl|3xl|4xl)", name):
        return rule(name, f"font-size:{FONT_SIZES[m.group(1)]}")

    # spacing
    if m := re.fullmatch(r"gap-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"gap:{val}")
    if m := re.fullmatch(r"p-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding:{val}")
    if m := re.fullmatch(r"px-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-left:{val};padding-right:{val}")
    if m := re.fullmatch(r"py-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-top:{val};padding-bottom:{val}")

    # padding per side (tokenized)
    if m := re.fullmatch(r"pr-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-right:{val}")
    if m := re.fullmatch(r"pl-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-left:{val}")
    if m := re.fullmatch(r"pt-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-top:{val}")
    if m := re.fullmatch(r"pb-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-bottom:{val}")

    # logical (RTL-aware)
    if m := re.fullmatch(r"ps-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-inline-start:{val}")
    if m := re.fullmatch(r"pe-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-inline-end:{val}")


    # ---- border widths FIRST ----
    if m := re.fullmatch(r"border-(0|2|4|8)", name):
        w = TOKENS["border_width"][m.group(1)]
        return rule(name, f"border-width:{w}")
    if m := re.fullmatch(r"border-(x|y)(?:-(0|2|4|8))?", name):
        axis, wkey = m.group(1), m.group(2) or "DEFAULT"
        w = TOKENS["border_width"][wkey]
        if axis == "x":
            return rule(name, f"border-left-width:{w};border-right-width:{w}")
        else:
            return rule(name, f"border-top-width:{w};border-bottom-width:{w}")
    if m := re.fullmatch(r"border-(t|r|b|l)(?:-(0|2|4|8))?", name):
        side, wkey = m.group(1), m.group(2) or "DEFAULT"
        w = TOKENS["border_width"][wkey]
        prop = {"t":"top","r":"right","b":"bottom","l":"left"}[side]
        return rule(name, f"border-{prop}-width:{w}")

    # ---- border colors by token/palette/name ----
    if m := re.fullmatch(r"border-([a-z0-9-]+)", name):
        key = m.group(1)

        # 1) exact token (e.g., slate-300)
        col = TOKENS["border_color"].get(key)
        if col is not None:
            return rule(name, f"border-color:{col}")

        # 2) built-in static palettes (red/blue/slate/green)
        if (pm := re.fullmatch(r"([a-z]+)-(\d{2,3})", key)):
            palette, step = pm.group(1), pm.group(2)
            pal = PALETTES.get(palette)
            if pal and step in pal:
                return rule(name, f"border-color:{pal[step]}")

        # 3) plain named color: border-red, border-green, etc.
        if re.fullmatch(r"[a-z]+", key):
            return rule(name, f"border-color:{key}")

        # No return here: fall through so theme variable palettes can handle
        # e.g., border-accent-500 → var(--accent-500)

    # rounded scale
    if m := re.fullmatch(r"rounded-([a-z0-9]+)", name):
        key = m.group(1); val = TOKENS["radius"].get(key)
        if val is not None:
            return rule(name, f"border-radius:{val}")
    if m := re.fullmatch(r"rounded-(t|r|b|l)-([a-z0-9]+)", name):
        side, key = m.group(1), m.group(2)
        val = TOKENS["radius"].get(key)
        if val is None:
            return None
        if side == "t":
            body = f"border-top-left-radius:{val};border-top-right-radius:{val}"
        elif side == "r":
            body = f"border-top-right-radius:{val};border-bottom-right-radius:{val}"
        elif side == "b":
            body = f"border-bottom-right-radius:{val};border-bottom-left-radius:{val}"
        else:
            body = f"border-top-left-radius:{val};border-bottom-left-radius:{val}"
        return rule(name, body)
    if m := re.fullmatch(r"rounded-(tl|tr|br|bl)-([a-z0-9]+)", name):
        corner, key = m.group(1), m.group(2)
        val = TOKENS["radius"].get(key)
        if val is None:
            return None
        prop = {"tl":"top-left","tr":"top-right","br":"bottom-right","bl":"bottom-left"}[corner]
        return rule(name, f"border-{prop}-radius:{val}")

    # --- margin scale ---
    if m := re.fullmatch(r"m-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin:{val}")
    if m := re.fullmatch(r"mx-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-left:{val};margin-right:{val}")
    if m := re.fullmatch(r"my-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-top:{val};margin-bottom:{val}")
    if m := re.fullmatch(r"mt-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-top:{val}")
    if m := re.fullmatch(r"mr-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-right:{val}")
    if m := re.fullmatch(r"mb-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-bottom:{val}")
    if m := re.fullmatch(r"ml-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-left:{val}")
    # logical (RTL-aware)
    if m := re.fullmatch(r"ms-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-inline-start:{val}")
    if m := re.fullmatch(r"me-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"margin-inline-end:{val}")

    # --- brand palette via theme variables ---
    # bg-brand-500 / text-brand-600 / border-brand-300
    if m := re.fullmatch(r"(bg|text|border)-brand-(\d{2,3})", name):
        prop, step = m.group(1), m.group(2)
        if prop == "bg":
            return rule(name, f"background:var(--brand-{step})")
        if prop == "text":
            return rule(name, f"color:var(--brand-{step})")
        if prop == "border":
            return rule(name, f"border-color:var(--brand-{step})")

    # theme palette → text-accent-600, text-brand-500, text-warning-400, etc.
    if m := re.fullmatch(r"text-([a-z]+)-(\d{2,3})", name):
        group, step = m.groups()
        return rule(name, f"color:var(--{group}-{step})")

    # optional: background palette → bg-accent-50, bg-brand-100, etc.
    if m := re.fullmatch(r"bg-([a-z]+)-(\d{2,3})", name):
        group, step = m.groups()
        return rule(name, f"background:var(--{group}-{step})")

    # you already handle borders; if not, mirror the same idea:
    # border-accent-500 → border-color: var(--accent-500)
    if m := re.fullmatch(r"border-([a-z]+)-(\d{2,3})", name):
        group, step = m.groups()
        return rule(name, f"border-color:var(--{group}-{step})")


    return None


def emit_arbitrary(name: str) -> str | None:
    esel = css_escape_class(name)

    # in emit_arbitrary(...)
    if m := re.fullmatch(r"aspect-\[(.+?)\]", name):
        return rule(css_escape_class(name), f"aspect-ratio:{m.group(1)}")

    # width
    if m := re.fullmatch(r"w-\[(.+?)\]", name):
        return rule(esel, f"width:{m.group(1)}")

    # padding
    if m := re.fullmatch(r"p-\[(.+?)\]", name):
        return rule(esel, f"padding:{m.group(1)}")
    if m := re.fullmatch(r"px-\[(.+?)\]", name):
        v = m.group(1); return rule(esel, f"padding-left:{v};padding-right:{v}")
    if m := re.fullmatch(r"py-\[(.+?)\]", name):
        v = m.group(1); return rule(esel, f"padding-top:{v};padding-bottom:{v}")
    
    # arbitrary per-side padding
    if m := re.fullmatch(r"pr-\[(.+?)\]", name):
        return rule(esel, f"padding-right:{m.group(1)}")
    if m := re.fullmatch(r"pl-\[(.+?)\]", name):
        return rule(esel, f"padding-left:{m.group(1)}")
    if m := re.fullmatch(r"pt-\[(.+?)\]", name):
        return rule(esel, f"padding-top:{m.group(1)}")
    if m := re.fullmatch(r"pb-\[(.+?)\]", name):
        return rule(esel, f"padding-bottom:{m.group(1)}")

    # logical (RTL-aware) arbitrary
    if m := re.fullmatch(r"ps-\[(.+?)\]", name):
        return rule(esel, f"padding-inline-start:{m.group(1)}")
    if m := re.fullmatch(r"pe-\[(.+?)\]", name):
        return rule(esel, f"padding-inline-end:{m.group(1)}")


    # colors & font-size (arbitrary)
    if m := re.fullmatch(r"text-\[(.+?)\]", name):
        raw = m.group(1)
        v = raw.replace("_", " ")
        # If it's a length or a calc()/clamp()/min()/max() expression → font-size
        if (
            re.fullmatch(r"\d+(?:\.\d+)?(px|rem|em|ch|ex|vh|vw|vmin|vmax|%)", v)
            or v.startswith(("calc(", "clamp(", "min(", "max("))
        ):
            return rule(esel, f"font-size:{v}")
        # Otherwise treat as a color
        return rule(esel, f"color:{v}")

    # size
    if m := re.fullmatch(r"h-\[(.+?)\]", name):
        return rule(css_escape_class(name), f"height:{m.group(1)}")

    # gap
    if m := re.fullmatch(r"gap-\[(.+?)\]", name):
        return rule(esel, f"gap:{m.group(1)}")

    # rounded arbitrary
    if m := re.fullmatch(r"rounded-\[(.+?)\]", name):
        return rule(esel, f"border-radius:{m.group(1)}")

    # shadow arbitrary (underscores become spaces)
    if m := re.fullmatch(r"shadow-\[(.+?)\]", name):
        return rule(esel, f"box-shadow:{m.group(1).replace('_',' ')}")

    # colors
    if m := re.fullmatch(r"bg-\[(.+?)\]", name):
        return rule(esel, f"background:{m.group(1).replace('_',' ')}")
    if m := re.fullmatch(r"text-\[(.+?)\]", name):
        return rule(esel, f"color:{m.group(1).replace('_',' ')}")

    # size
    if m := re.fullmatch(r"h-\[(.+?)\]", name):
        return rule(css_escape_class(name), f"height:{m.group(1)}")

    # grid template columns: grid-cols-[280px_1fr]  (underscores -> spaces)
    if m := re.fullmatch(r"grid-cols-\[(.+?)\]", name):
        v = m.group(1).replace("_", " ")
        return rule(css_escape_class(name), f"grid-template-columns:{v}")

    # grid template rows: grid-rows-[auto_1fr]  (underscores -> spaces)
    if m := re.fullmatch(r"grid-rows-\[(.+?)\]", name):
        v = m.group(1).replace("_", " ")
        return rule(css_escape_class(name), f"grid-template-rows:{v}")

    # z-index arbitrary
    if m := re.fullmatch(r"z-\[(.+?)\]", name):
        return rule(esel, f"z-index:{m.group(1)}")

    if m := re.fullmatch(r"top-\[(.+?)\]", name):
        return rule(esel, f"top:{m.group(1)}")

    # --- border arbitrary: width OR color ---
    if m := re.fullmatch(r"border-\[(.+?)\]", name):
        v = m.group(1).replace("_", " ")
        # length? → width (px/rem/em/ch/ex/vh/vw/%)
        if re.fullmatch(r"\d+(?:\.\d+)?(px|rem|em|ch|ex|vh|vw|%)", v):
            return rule(esel, f"border-width:{v}")
        # otherwise treat as color (names, rgb/rgba/hsl/hsla, hex)
        return rule(esel, f"border-color:{v}")

    # explicit arbitrary border color
    if m := re.fullmatch(r"border-color-\[(.+?)\]", name):
        return rule(esel, f"border-color:{m.group(1).replace('_',' ')}")

    # --- margin arbitrary (supports logical too) ---
    if m := re.fullmatch(r"m-\[(.+?)\]", name):
        return rule(esel, f"margin:{m.group(1)}")
    if m := re.fullmatch(r"mx-\[(.+?)\]", name):
        v = m.group(1); return rule(esel, f"margin-left:{v};margin-right:{v}")
    if m := re.fullmatch(r"my-\[(.+?)\]", name):
        v = m.group(1); return rule(esel, f"margin-top:{v};margin-bottom:{v}")
    if m := re.fullmatch(r"mt-\[(.+?)\]", name):
        return rule(esel, f"margin-top:{m.group(1)}")
    if m := re.fullmatch(r"mr-\[(.+?)\]", name):
        return rule(esel, f"margin-right:{m.group(1)}")
    if m := re.fullmatch(r"mb-\[(.+?)\]", name):
        return rule(esel, f"margin-bottom:{m.group(1)}")
    if m := re.fullmatch(r"ml-\[(.+?)\]", name):
        return rule(esel, f"margin-left:{m.group(1)}")
    if m := re.fullmatch(r"ms-\[(.+?)\]", name):
        return rule(esel, f"margin-inline-start:{m.group(1)}")
    if m := re.fullmatch(r"me-\[(.+?)\]", name):
        return rule(esel, f"margin-inline-end:{m.group(1)}")

    # transition arbitrary (underscores become spaces)
    if m := re.fullmatch(r"transition-\[(.+?)\]", name):
        return rule(esel, f"transition:{m.group(1).replace('_',' ')}")

    # background-image (DO NOT replace underscores)
    if m := re.fullmatch(r"bg-image-\[(.+?)\]", name):
        return rule(esel, f"background-image:{m.group(1)}")

    return None

# --- variants ---
def wrap_variant(sel: str, css: str, variant: str) -> str:
    esel = css_escape_class(sel)
    if variant in BPS:
        return f"@media {BPS[variant]}{{{css}}}"
    if variant == "hover":
        return css.replace(f".{esel}{{", f".{variant}\\:{esel}:hover{{")
    if variant == "focus":
        return css.replace(f".{esel}{{", f".{variant}\\:{esel}:focus{{")
    return css

def emit_one(cls: str) -> str | None:
    parts = cls.split(":")
    base = parts[-1]
    variants = parts[:-1]

    css = emit_base(base) or emit_scale(base) or emit_arbitrary(base)
    if not css:
        return None
    for v in reversed(variants):
        css = wrap_variant(base, css, v)
    return css

def compile_used_css() -> str:
    out: list[str] = []
    for cls in sorted(_used):
        css = emit_one(cls)
        if css:
            out.append(css)
    return "\n".join(out)
