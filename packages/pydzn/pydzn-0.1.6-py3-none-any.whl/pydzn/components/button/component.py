from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport
from pydzn.htmx import HtmxSupport


class Button(VariantSupport, BaseComponent, HtmxSupport):
    """
    Server-rendered Button with pluggable variants/sizes.

    - Built-in variants keep colors inline so it works without a theme pack.
    - You can add external libraries and select with namespace, e.g. variant="acme:glass".
    """

    # visual “structures” (kept color-aware so no theme pack needed)
    VARIANTS = {
        # solid
        "solid-primary": (
            "rounded-sm border border-transparent "
            "bg-[#2563eb] text-[white] "
            "shadow-md hover:shadow-lg"
        ),
        # outline
        "outline-primary": (
            "rounded-sm border-2 border-blue-500 "
            "bg-[transparent] text-[#2563eb] "
            "shadow-sm hover:shadow-md"
        ),
        # ghost (neutral)
        "ghost-neutral": (
            "rounded-sm border-0 "
            "bg-[transparent] text-body "
            "shadow-none hover:bg-[rgba(15,23,42,.06)]"
        ),
        # linky button
        "link-primary": (
            "rounded-none border-0 "
            "bg-[transparent] text-[#2563eb] "
            "shadow-none hover:underline"
        ),
    }

    # density
    SIZES = {
        "sm": "px-3 py-1",
        "md": "px-5 py-2",
        "lg": "px-6 py-3",
        "xl": "px-8 py-4",
    }

    # tones are optional here; variants carry color already
    TONES = {}

    # project-wide defaults can be overridden via VariantSupport.set_default_choices(Button, ...)
    DEFAULTS = {
        "variant": "",
        "size": "md",
        "tone": "",
    }

    def __init__(
        self,
        text: str = "",
        children: str | None = None,
        *,
        tag: str = "button",
        # variant system
        variant: str | None = None,
        size: str | None = None,
        tone: str | None = None,
        # raw utility escape hatch (merged last)
        dzn: str | None = None,
        **attrs,
    ):
        # allow stray attrs["dzn"] too
        extra_dzn = dzn or attrs.pop("dzn", None)

        # resolve VARIANT + SIZE (+ optional TONE) + extra_dzn
        effective_dzn = self._resolve_variant_dzn(
            variant=variant,
            size=size,
            tone=tone,
            extra_dzn=extra_dzn,
        )

        super().__init__(children=children, tag=tag, dzn=effective_dzn, **attrs)
        self.text = text

    def as_link(self, href: str, *, new_tab: bool=False):
            self.tag = "a"
            self.html_attrs["href"] = href
            self.html_attrs["role"] = "link"
            if new_tab:
                self.html_attrs["target"] = "_blank"
                self.html_attrs["rel"] = "noopener noreferrer"
            return self
            
    def context(self) -> dict:
        return {"text": self.text}
