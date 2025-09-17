from __future__ import annotations
import uuid
import re
from typing import Dict, Optional, Tuple

# Default breakpoints (smartphone/tablet/desktop)
# (min_px, max_px) — use None for unbounded side
DEFAULT_BREAKPOINTS: Dict[str, Tuple[Optional[int], Optional[int]]] = {
    "mobile":  (None, 767),
    "tablet":  (768, 1023),
    "desktop": (1024, None),
}


def _safe(label: str) -> str:
    """
    Make a label safe for use in a CSS class selector.
    """
    s = re.sub(r'[^a-zA-Z0-9_-]+', '-', label.strip()).strip('-')
    return s or "view"


def _mq(min_px: Optional[int], max_px: Optional[int]) -> str:
    """
    Build a media query prefix for given min/max.
    """
    if min_px is None and max_px is None:
        # No query → applies to all widths (rare; avoid if you want exclusivity)
        return ""
    if min_px is None:
        return f"@media (max-width:{max_px}px)"
    if max_px is None:
        return f"@media (min-width:{min_px}px)"
    return f"@media (min-width:{min_px}px) and (max-width:{max_px}px)"


def responsive_pair(desktop_html: str, mobile_html: str, md_min_px: int = 768) -> str:
    """Return both DOM trees with CSS that shows exactly one, scoped to a unique wrapper."""
    uid = uuid.uuid4().hex[:8]
    cls = f"resp-pair-{uid}"
    css = f"""
<style>
.{cls} ._desktop {{ display: none; }}
.{cls} ._mobile  {{ display: block; }}
@media (min-width:{md_min_px}px) {{
  .{cls} ._desktop {{ display: block; }}
  .{cls} ._mobile  {{ display: none;  }}
}}
</style>
"""
    return (
        css
        + f'<div class="{cls}">'
        + f'  <div class="_mobile">{mobile_html}</div>'
        + f'  <div class="_desktop">{desktop_html}</div>'
        + f'</div>'
    )


def responsive_triple(
    *,
    desktop: str,
    tablet: str,
    mobile: str,
    tablet_min_px: int = 768,
    desktop_min_px: int = 1024,
) -> str:
    """
    Convenience: desktop/tablet/mobile with sensible defaults.
    """
    bps = {
        "mobile":  (None, tablet_min_px - 1),
        "tablet":  (tablet_min_px, desktop_min_px - 1),
        "desktop": (desktop_min_px, None),
    }
    return responsive_multi(
        breakpoints=bps,
        mobile=mobile,
        tablet=tablet,
        desktop=desktop,
    )


def responsive_multi(
    *,
    breakpoints: Optional[Dict[str, Tuple[Optional[int], Optional[int]]]] = None,
    **views: str,
) -> str:
    """
    Arbitrary number of responsive views.

    Usage:
        html = responsive_multi(
            desktop=desktop_html,
            tablet=tablet_html,
            mobile=mobile_html,
            breakpoints={
                "mobile":  (None, 767),
                "tablet":  (768, 1023),
                "desktop": (1024, None),
            },
        )

    - Pass any number of named views as keyword args (order is preserved).
    - 'breakpoints' maps the same names → (min_px, max_px). Use None for unbounded.
    - If 'breakpoints' is omitted, defaults to DEFAULT_BREAKPOINTS and requires
      your views to be some subset/superset of {"mobile","tablet","desktop"}.
    """
    if not views:
        raise ValueError("responsive_multi: provide at least one named view (e.g., desktop=..., mobile=...)")

    # Keep insertion order (Python 3.7+ dicts are ordered)
    ordered = list(views.items())

    bps = dict(breakpoints or DEFAULT_BREAKPOINTS)

    # Validate that we have a breakpoint for every view name
    missing = [name for name, _ in ordered if name not in bps]
    if missing:
        raise ValueError(
            "responsive_multi: missing breakpoints for: "
            + ", ".join(missing)
            + ". Provide breakpoints={...} with entries for each view."
        )

    uid = uuid.uuid4().hex[:8]
    cls = f"resp-multi-{uid}"

    # Base: hide all views
    lines = [f".{cls} [class^=\"_view-\"], .{cls} [class*=\" _view-\"] {{ display:none; }}"]

    # Show each view within its media query
    for name, _html in ordered:
        min_px, max_px = bps[name]
        sel = f".{cls} ._view-{_safe(name)}"
        mq = _mq(min_px, max_px)
        if mq:
            lines.append(f"{mq} {{ {sel} {{ display:block; }} }}")
        else:
            # No bounds → always show (use with care; will conflict with others)
            lines.append(f"{sel} {{ display:block; }}")

    css = "<style>\n" + "\n".join(lines) + "\n</style>\n"

    # Emit wrapper + each view
    out = [css, f'<div class="{cls}">']
    for name, html_str in ordered:
        out.append(f'  <div class="_view-{_safe(name)}">{html_str}</div>')
    out.append("</div>")
    return "\n".join(out)
