import uuid, re
from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport
from pydzn.dzn import register_dzn_classes


def _hamburger_svg(sz=24):
    return f'''
<svg width="{sz}" height="{sz}" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <rect x="3" y="6"  width="18" height="2" rx="1" fill="currentColor"/>
  <rect x="3" y="11" width="18" height="2" rx="1" fill="currentColor"/>
  <rect x="3" y="16" width="18" height="2" rx="1" fill="currentColor"/>
</svg>
'''.strip()

def _close_svg(sz=24):
    return f'''
<svg width="{sz}" height="{sz}" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
'''.strip()


class HamburgerMenu(VariantSupport, BaseComponent):
    VARIANTS = {
        # Trigger styles
        "trigger:quiet": (
            "px-3 py-2 rounded-md border-0 "
            "bg-[transparent] text-[#333] hover:text-[#6b6969] cursor-pointer"
        ),
        "trigger:solid": (
            "px-3 py-2 rounded-md border border-[1px] "
            "bg-[#2563eb] text-[white] hover:bg-[rgba(37,99,235,.92)] cursor-pointer"
        ),

        # Panel styles: no default background here
        "panel:sheet": "text-[black] shadow-xl rounded-[10px]",
        "panel:glass": "text-[black] shadow-lg rounded-[10px] backdrop-blur bg-[rgba(255,255,255,.70)]",
        "panel:bare":  "text-[inherit] shadow-none",
    }

    def __init__(self, *,
        children: str = "",
        mode: str = "right",
        drawer_width: int | str = 320,
        dropdown_height: int | str = 320,
        show_backdrop: bool = True,
        icon_size: int = 24,
        trigger_variant: str | None = None,
        trigger_size: str | None = None,
        panel_variant: str | None = None,
        dzn: str | None = None,
        button_dzn: str | None = None,
        panel_dzn: str | None = None,
        **attrs,
    ):
        self._uid = uuid.uuid4().hex[:8]
        self.mode = mode
        self.drawer_width = int(drawer_width)
        self.dropdown_height = int(dropdown_height)
        self.show_backdrop = bool(show_backdrop)
        self.icon_size = int(icon_size)

        # Resolve trigger/panel via VariantSupport
        self._trigger_dzn = self._resolve_variant_dzn(
            variant=trigger_variant or "trigger:quiet",
            size=trigger_size or "md",
            tone=None,
            extra_dzn=(button_dzn or "")
        )
        self._panel_dzn = self._resolve_variant_dzn(
            variant=panel_variant or "panel:sheet",
            size=None,
            tone=None,
            extra_dzn=(panel_dzn or "")
        )

        # Wrapper classes + auto-forward visual tokens to the panel
        wrapper_core = "relative inline-block"
        base_wrapper = f"{wrapper_core} {dzn.strip()}" if dzn else wrapper_core
        forwarded = self._extract_visual_tokens(dzn or "")
        self._panel_forwarded = forwarded

        # Register for /_dzn.css emission
        register_dzn_classes(base_wrapper)
        register_dzn_classes(self._trigger_dzn)
        register_dzn_classes(self._panel_dzn)
        register_dzn_classes(self._panel_forwarded)
        register_dzn_classes(
            "flex items-center gap-2 hidden fixed inset-0 absolute top-0 bottom-0 "
            "right-0 left-0 block overflow-auto border rounded-[10px] "
            "z-[10000] z-[10001]"
        )

        super().__init__(children=children, tag="div", dzn=base_wrapper, **attrs)

    def context(self) -> dict:
        return {}

    # --- helpers ---
    @staticmethod
    def _extract_visual_tokens(s: str) -> str:
        if not s: return ""
        keep = []
        for cls in s.split():
            if (cls.startswith("bg-[") or cls.startswith("text-[")
                or cls.startswith("border") or cls.startswith("rounded")
                or cls.startswith("shadow")):
                keep.append(cls)
        return " ".join(keep)

    @staticmethod
    def _has_bg_token(s: str) -> bool:
        return bool(re.search(r"\bbg-\[", s or ""))

    # --- render ---
    def render(self) -> str:
        uid = self._uid
        root_cls = f"hm-{uid}"
        cb_id = f"hmcb-{uid}"
        drawer_id = f"hm-drawer-{uid}"

        css = f"""
<style>
.{root_cls} .hm__icon--close {{ display:none; }}
.{root_cls} input[type="checkbox"] {{ position:absolute; opacity:0; pointer-events:none; }}
.{root_cls} .hm__toggle {{ display:inline-flex; align-items:center; gap:.5rem; }}

.{root_cls} .hm__drawer {{
  transition: transform .22s ease, opacity .22s ease;
  will-change: transform, opacity;
  outline: none;
}}
.{root_cls}[data-mode="right"]  .hm__drawer {{ transform: translateX(100%);  }}
.{root_cls}[data-mode="left"]   .hm__drawer {{ transform: translateX(-100%); }}
.{root_cls}[data-mode="dropdown"] .hm__drawer {{ transform: translateY(-8px); opacity:0; }}

.{root_cls} input:checked ~ label .hm__icon--hamburger {{ display:none; }}
.{root_cls} input:checked ~ label .hm__icon--close     {{ display:inline-block; }}

.{root_cls}[data-mode="right"]    input:checked ~ .hm__backdrop {{ display:block; }}
.{root_cls}[data-mode="left"]     input:checked ~ .hm__backdrop {{ display:block; }}
.{root_cls}[data-mode="dropdown"] .hm__backdrop {{ display:none !important; }}

.{root_cls}[data-mode="right"]    input:checked ~ .hm__drawer {{ transform: translateX(0);  }}
.{root_cls}[data-mode="left"]     input:checked ~ .hm__drawer {{ transform: translateX(0);  }}
.{root_cls}[data-mode="dropdown"] input:checked ~ .hm__drawer {{ transform: translateY(0); opacity:1; }}
</style>
""".strip()

        backdrop_html = ""
        if self.show_backdrop and self.mode in ("left", "right"):
            backdrop_html = (
                f'<label for="{cb_id}" class="hm__backdrop hidden fixed inset-0 bg-[rgba(0,0,0,.35)] z-[10000]" aria-hidden="true"></label>'
            )

        trigger_html = f"""
<label for="{cb_id}" class="hm__toggle {self._trigger_dzn} flex items-center gap-2" aria-controls="{drawer_id}" aria-haspopup="true" style="cursor:pointer">
  <span class="hm__icon hm__icon--hamburger" aria-hidden="true">{_hamburger_svg(self.icon_size)}</span>
  <span class="hm__icon hm__icon--close z-[10002]" aria-hidden="true">{_close_svg(self.icon_size)}</span>
</label>
""".strip()

        # Drawer base position/size
        if self.mode in ("left", "right"):
            side = "right-0" if self.mode == "right" else "left-0"
            drawer_base = f"fixed top-0 bottom-0 {side} overflow-auto z-[10001] w-[{self.drawer_width}px]"
        else:
            drawer_base = (
                f"absolute top-[calc(100%+8px)] right-0 "
                f"h-[{self.dropdown_height}px] w-[min(92vw,420px)] "
                f"overflow-auto border rounded-[10px] z-[10001]"
            )
        register_dzn_classes(drawer_base)

        # Panel classes = variant + forwarded visual tokens (+ default bg if none provided)
        panel_classes = f"{self._panel_dzn} {self._panel_forwarded}".strip()
        if not self._has_bg_token(panel_classes):
            panel_classes = f"{panel_classes} bg-[white]"
        register_dzn_classes(panel_classes)

        drawer_html = f"""
<div id="{drawer_id}" class="hm__drawer {drawer_base} {panel_classes}">
  {self.children or ""}
</div>
""".strip()

        checkbox = f'<input id="{cb_id}" type="checkbox" />'

        return (
            css
            + f'<div class="{root_cls}" data-mode="{self.mode}" {self._attrs_string()}>'
            + checkbox
            + trigger_html
            + backdrop_html
            + drawer_html
            + "</div>"
        )

    def _attrs_string(self) -> str:
        import html as _html
        attr_parts = []
        for k, v in self.html_attrs.items():
            if k == "style":
                continue
            attr_parts.append(f'{k}="{_html.escape(str(v), quote=True)}"')
        style_str = self._style_string()
        if style_str:
            attr_parts.append(f'style="{_html.escape(style_str, quote=True)}"')
        return " ".join(attr_parts)
