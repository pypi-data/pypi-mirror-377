from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport
from pydzn.dzn import register_dzn_classes


class NavItem(VariantSupport, BaseComponent):
    """
    Nav item with pluggable variants + fluent helpers so users don't need DZN utilities.

    Example:
      NavItem(variant="sidebar-underline", children=Text("Overview").render())
        .center()
        .height(64)
        .full_width()
        .bottom_divider("subtle")
        .hover(bg="rgba(37,99,235,.06)", text="#2563eb", underline="blue-500")
        .focus(bg="rgba(37,99,235,.10)")
        .render()
    """

    # -------- Variants --------
    VARIANTS = {
        # empty key → no styles when variant is ""
        "": "",

        # Sidebar family
        "sidebar-default": (
            "flex items-center justify-center text-center "
            "rounded-none border-solid border-b border-subtle "
            "text-body hover:bg-[rgba(15,23,42,.06)]"
        ),
        "sidebar-compact": (
            "flex items-center justify-center text-center "
            "rounded-none border-solid border-b border-subtle "
            "text-body hover:bg-[rgba(15,23,42,.06)]"
        ),
        "sidebar-active": (
            "flex items-center justify-center text-center "
            "rounded-none border-solid border-b border-subtle "
            "bg-[rgba(37,99,235,.10)] text-[#2563eb]"
        ),
        "sidebar-quiet": (
            "flex items-center justify-center text-center "
            "rounded-none border-solid border-b border-subtle "
            "text-[rgb(100,116,139)] hover:bg-[rgba(15,23,42,.04)]"
        ),
        # underline-only (no box borders)
        "sidebar-underline": (
            "flex items-center justify-center text-center "
            "rounded-none border-0 border-b border-subtle border-solid py-2"
        ),
        # square tile w/ underline + hovers
        "sidebar-squared-underline": (
            "flex items-center justify-center text-center "
            "rounded-none border-0 border-b border-subtle border-solid py-2 "
            "hover:bg-[rgba(37,99,235,.06)] hover:border-blue-500 hover:text-[#2563eb] "
            "focus:bg-[rgba(37,99,235,.10)]"
        ),

        # Dropdown family
        "dropdown-item": (
            "px-3 py-2 rounded-md border-0 "
            "bg-[transparent] text-body hover:bg-[rgba(15,23,42,.06)]"
        ),
        "dropdown-accent": (
            "w-[100%] px-3 py-2 rounded-md border-0 "
            "bg-[transparent] text-[#2563eb] hover:bg-[rgba(37,99,235,.08)]"
        ),
        "dropdown-danger": (
            "w-[100%] px-3 py-2 rounded-md border-0 "
            "bg-[transparent] text-[rgb(239,68,68)] hover:bg-[rgba(239,68,68,.08)]"
        ),
        "dropdown-plain": (
            "w-[100%] px-3 py-2 rounded-none border-0 "
            "bg-[transparent] text-body hover:bg-[rgba(15,23,42,.04)]"
        ),

        # Simple family
        "simple-item": (
            "px-3 py-2 rounded-none border-0 bg-[transparent] no-underline "
            "text-[#333] hover:text-[#6b6969]"
        ),

    }

    SIZES = {
        "sm": "text-[12px]",
        "md": "text-[14px]",
        "lg": "text-[16px]",
    }

    TONES = {
        "muted":   "text-[rgb(100,116,139)]",
        "primary": "text-[#2563eb]",
        "danger":  "text-[rgb(239,68,68)]",
    }

    DEFAULTS = {"variant": "", "size": "md", "tone": ""}

    # -------- ctor --------
    def __init__(
        self,
        *,
        children: str | None = None,
        tag: str = "div",
        variant: str | None = None,
        size: str | None = None,
        tone: str | None = None,
        dzn: str | None = None,   # extra raw utilities merged last
        **attrs,
    ):
        extra_dzn = dzn or attrs.pop("dzn", None)

        # minimal a11y defaults
        attrs.setdefault("role", "button")
        attrs.setdefault("tabindex", "0")

        base = self._resolve_variant_dzn(
            variant=variant,
            size=size,
            tone=tone,
            extra_dzn=extra_dzn,
        )

        # keep base vs. runtime styles separate
        self._base_dzn = base.strip()
        self._runtime_dzn: list[str] = []

        # pre-register everything we know at init
        register_dzn_classes(self._base_dzn)

        # let BaseComponent merge base dzn into class
        super().__init__(children=children or "", tag=tag, dzn=self._base_dzn, **attrs)

    # -------- internal helpers --------
    def _merge_all(self) -> str:
        return " ".join([self._base_dzn] + self._runtime_dzn).strip()

    def _add_runtime(self, *classes: str) -> None:
        cls_str = " ".join(c for c in classes if c)
        if not cls_str:
            return
        # register for CSS emission
        register_dzn_classes(cls_str)
        # track runtime classes
        self._runtime_dzn.extend(c for c in cls_str.split() if c)
        # immediately apply to html_attrs["class"] so render sees it
        merged = self._merge_all()
        self.html_attrs["class"] = self._merge_classes(self.html_attrs.get("class", ""), merged)

    # -------- fluent builder methods --------
    def center(self, *, x: bool = True, y: bool = True, text: bool = True):
        if x or y:
            self._add_runtime("flex")
        if x:
            self._add_runtime("justify-center")
        if y:
            self._add_runtime("items-center")
        if text:
            self._add_runtime("text-center")
        return self

    def height(self, px: int):
        self._add_runtime(f"h-[{px}px]")
        return self

    def full_width(self, on: bool = True):
        if on:
            self._add_runtime("w-[100%]")
        return self

    def bottom_divider(self, color: str = "subtle", *, style: str = "solid"):
        # ensure only the bottom edge shows
        self._add_runtime("border-0", "border-b", f"border-{color}", f"border-{style}")
        return self

    def hover(self, *, bg: str | None = None, text: str | None = None, underline: str | None = None):
        if bg:
            self._add_runtime(f"hover:bg-[{bg}]")
        if text:
            self._add_runtime(f"hover:text-[{text}]")
        if underline:
            self._add_runtime(f"hover:border-{underline}")
        return self

    def focus(self, *, bg: str | None = None):
        if bg:
            self._add_runtime(f"focus:bg-[{bg}]")
        return self

    def padding(self, *, all: int | str | None = None, x: int | str | None = None, y: int | str | None = None):
        def _choose(prefix: str, val):
            if val is None:
                return
            if isinstance(val, int):
                self._add_runtime(f"{prefix}-{val}")
            else:
                self._add_runtime(f"{prefix}-[{val}]")
        _choose("p", all)
        _choose("px", x)
        _choose("py", y)
        return self

    def reset_runtime_styles(self):
        """Remove everything added by builder methods (keeps the chosen variant)."""
        self._runtime_dzn = []
        # reset class to just base
        self.html_attrs["class"] = self._base_dzn
        register_dzn_classes(self._base_dzn)
        return self

    def as_link(self, href: str, *, new_tab: bool=False):
        self.tag = "a"
        self.html_attrs["href"] = href
        self.html_attrs["role"] = "link"
        if new_tab:
            self.html_attrs["target"] = "_blank"
            self.html_attrs["rel"] = "noopener noreferrer"
        return self

    def no_underline(self, all_states: bool = True):
        self._add_runtime("no-underline")
        if all_states:
            self._add_runtime("hover:no-underline", "focus:no-underline")
        return self

    # required by BaseComponent
    def context(self) -> dict:
        return {}
