from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport


class Sidebar(VariantSupport, BaseComponent):
    """
    Sidebar container with pluggable variants.
    NOTE: No side-specific borders/shadows here — the layout decides the divider/shadow.
    """

    # Visual “shells” (theme-aware names play nice if your theme defines bg-elevated/bg-surface/etc.)
    VARIANTS = {
        # transparent shells
        "bare":            "bg-[transparent] shadow-none border-0",
        "ghost":           "bg-[transparent] shadow-none",

        # neutral panels
        "panel":           "bg-elevated shadow-none",
        "panel-soft":      "bg-[rgba(15,23,42,.03)] shadow-none",
        "panel-elevated":  "bg-elevated shadow-sm",
        "panel-elevated-lg":"bg-elevated shadow-md",
        "muted":           "bg-surface shadow-none",

        # fun
        "glass":           "bg-[rgba(255,255,255,.6)] shadow-sm",
    }

    # Inner padding “sizes”
    SIZES = {
        "xs": "p-2",
        "sm": "p-3",
        "md": "p-4",
        "lg": "p-6",
    }

    # Tones optional (left empty since variants already choose a look)
    TONES = {}

    # Project-wide defaults (overridable via VariantSupport.set_default_choices)
    DEFAULTS = {
        "variant": "panel",
        "size": "md",
        "tone": "",
    }

    def __init__(
        self,
        *,
        children: str | None = None,
        tag: str = "aside",
        variant: str | None = None,
        size: str | None = None,
        tone: str | None = None,
        dzn: str | None = None,    # extra raw utilities merged last
        **attrs,
    ):
        # allow stray attrs["dzn"]
        extra_dzn = dzn or attrs.pop("dzn", None)

        effective_dzn = self._resolve_variant_dzn(
            variant=variant,
            size=size,
            tone=tone,
            extra_dzn=extra_dzn,
        )

        super().__init__(children=children or "", tag=tag, dzn=effective_dzn, **attrs)

    def context(self) -> dict:
        return {}
