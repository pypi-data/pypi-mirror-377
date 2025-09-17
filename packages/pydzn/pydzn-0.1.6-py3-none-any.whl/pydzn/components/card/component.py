from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport
from pydzn.htmx import HtmxSupport


class Card(VariantSupport, BaseComponent, HtmxSupport):
    """
    Server-rendered Card with pluggable variants/sizes/tones.
    Variants focus on layout/structure; tones mainly adjust border color.
    """

    # visual “structures”
    VARIANTS = {
        "panel": (
            "flex flex-col gap-4 p-4 rounded-xl "
            "border border-subtle bg-elevated shadow-sm"
        ),
        "plain": (
            "flex flex-col gap-3 p-4 rounded-md "
            "border border-subtle bg-surface shadow-none"
        ),
        "elevated": (
            "flex flex-col gap-4 p-4 rounded-xl "
            "border border-transparent bg-elevated shadow-lg"
        ),
        "outlined": (
            "flex flex-col gap-4 p-4 rounded-lg "
            "border-2 border-slate-300 bg-[transparent] shadow-none"
        ),
        "soft": (
            "flex flex-col gap-4 p-4 rounded-xl "
            "border-0 bg-[rgba(15,23,42,.03)] shadow-sm"
        ),
        "glass": (
            "flex flex-col gap-4 p-4 rounded-xl "
            "border border-[rgba(255,255,255,.25)] bg-[rgba(255,255,255,.08)] shadow-md"
        ),
        "ghost": (
            "flex flex-col gap-4 p-4 rounded-md "
            "border-0 bg-[transparent] shadow-none"
        ),
    }

    # density
    SIZES = {
        "xs": "p-2 gap-2 rounded-sm",
        "sm": "p-3 gap-2 rounded-md",
        "md": "p-4 gap-3 rounded-lg",
        "lg": "p-6 gap-4 rounded-xl",
        "xl": "p-8 gap-5 rounded-2xl",
    }

    # tones mainly drive border color (kept subtle by default)
    TONES = {
        "neutral": "border-subtle",
        "primary": "border-blue-500",
        "success": "border-green-500",
        "danger":  "border-red-500",
    }

    # project-wide defaults can be overridden at runtime:
    #   Card.set_default_choices(variant="...", size="...", tone="...")
    DEFAULTS = {
        "variant": "panel",
        "size": "md",
        "tone": "neutral",
    }

    def __init__(
        self,
        children: str | None = None,
        *,
        tag: str = "div",
        # variant system
        variant: str | None = None,
        size: str | None = None,
        tone: str | None = None,
        # raw utility escape hatch (merged last)
        dzn: str | None = None,
        **attrs,
    ):
        extra_dzn = dzn or attrs.pop("dzn", None)

        effective_dzn = self._resolve_variant_dzn(
            variant=variant,
            size=size,
            tone=tone,
            extra_dzn=extra_dzn,
        )

        super().__init__(children=children, tag=tag, dzn=effective_dzn, **attrs)

    def context(self) -> dict:
        return {}
