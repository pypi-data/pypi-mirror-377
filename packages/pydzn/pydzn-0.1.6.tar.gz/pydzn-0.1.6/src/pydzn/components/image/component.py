from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport
from pydzn.htmx import HtmxSupport
from pydzn.dzn import register_dzn_classes


class Img(VariantSupport, BaseComponent, HtmxSupport):
    """
    Server-rendered <img> with pluggable variants/sizes and fluent helpers.

    Notes:
      - No default variant is applied. Use helpers or pass `dzn=...`.
      - Object-fit / object-position are set via inline style for reliability
    """

    # Common visual structures (kept color-neutral)
    VARIANTS = {
        # Full-width, keep intrinsic aspect ratio.
        "responsive": (
            "block w-[100%] h-s[auto]"
        ),
        # Small avatar (circle, cropped fill)
        "avatar-sm": (
            "block rounded-full w-[32px] h-[32px] border border-subtle shadow-sm"
        ),
        # Medium avatar
        "avatar-md": (
            "block rounded-full w-[40px] h-[40px] border border-subtle shadow-sm"
        ),
        # Large avatar
        "avatar-lg": (
            "block rounded-full w-[64px] h-[64px] border border-subtle shadow-md"
        ),
        # Polaroid-like thumbnail
        "thumbnail": (
            "block rounded-md w-[160px] h-[auto] border border-subtle shadow-sm"
        ),
        # Card media (fixed height crop)
        "card-media": (
            "block w-[100%] h-[200px] rounded-md border-0 shadow-sm"
        ),
        # Logo (height-driven, no borders)
        "logo": (
            "inline-block h-[32px] w-[auto]"
        ),
    }

    # Optional density presets that focus on size only
    SIZES = {
        "sm": "w-[120px] h-[auto]",
        "md": "w-[240px] h-[auto]",
        "lg": "w-[480px] h-[auto]",
        "xl": "w-[720px] h-[auto]",
    }

    # Images don’t generally need tones; keep empty
    TONES = {}

    # **No default variant or size by default**
    DEFAULTS = {"variant": "", "size": "", "tone": ""}

    def __init__(
        self,
        src: str = "",
        alt: str = "",
        *,
        tag: str = "img",
        # variants
        variant: str | None = None,
        size: str | None = None,
        tone: str | None = None,
        # extra raw utilities merged last
        dzn: str | None = None,
        # common <img> attributes
        width: int | str | None = None,
        height: int | str | None = None,
        loading: str | None = None,        # "lazy" | "eager"
        decoding: str | None = None,       # "async" | "sync" | "auto"
        fetchpriority: str | None = None,  # "high" | "low" | "auto"
        referrerpolicy: str | None = None, # e.g., "no-referrer"
        crossorigin: str | None = None,    # "anonymous" | "use-credentials"
        draggable: bool | None = None,
        **attrs,
    ):
        extra_dzn = dzn or attrs.pop("dzn", None)

        # Resolve DZN from variant/size/tone + extra
        base_dzn = self._resolve_variant_dzn(
            variant=variant,
            size=size,
            tone=tone,
            extra_dzn=extra_dzn,
        ).strip()

        # Initialize as an <img> (void element; BaseComponent will handle tag)
        attrs.setdefault("src", src)
        attrs.setdefault("alt", alt)

        if width is not None:
            attrs["width"] = width
        if height is not None:
            attrs["height"] = height
        if loading:
            attrs["loading"] = loading
        if decoding:
            attrs["decoding"] = decoding
        if fetchpriority:
            attrs["fetchpriority"] = fetchpriority
        if referrerpolicy:
            attrs["referrerpolicy"] = referrerpolicy
        if crossorigin:
            attrs["crossorigin"] = crossorigin
        if draggable is not None:
            attrs["draggable"] = "true" if draggable else "false"

        # Track base vs runtime classes (like NavItem)
        self._base_dzn = base_dzn
        self._runtime_dzn: list[str] = []

        # Pre-register CSS classes for emission
        if self._base_dzn:
            register_dzn_classes(self._base_dzn)

        super().__init__(children=None, tag=tag, dzn=self._base_dzn, **attrs)

    # ---------- fluent: apply variant/size/tone after init ----------
    def variant(self, name: str):
        """Apply a variant by name (supports namespaced libraries registered via VariantSupport)."""
        if not name:
            return self
        dzn = self._resolve_variant_dzn(variant=name, size=None, tone=None, extra_dzn=None).strip()
        if dzn:
            self._add_runtime(dzn)
        return self

    # ---------- internals ----------
    def _merge_all(self) -> str:
        return " ".join([self._base_dzn] + self._runtime_dzn).strip()

    def _add_runtime(self, *classes: str) -> None:
        cls_str = " ".join(c for c in classes if c)
        if not cls_str:
            return
        register_dzn_classes(cls_str)
        self._runtime_dzn.extend(c for c in cls_str.split() if c)
        merged = self._merge_all()
        # BaseComponent should have html_attrs and class merge like NavItem uses
        self.html_attrs["class"] = self._merge_classes(self.html_attrs.get("class", ""), merged)

    def _append_style(self, css_snippet: str) -> None:
        if not css_snippet:
            return
        cur = (self.html_attrs.get("style") or "").strip()
        if cur and not cur.endswith(";"):
            cur += ";"
        self.html_attrs["style"] = f"{cur}{css_snippet}"

    # ---------- fluent helpers (return self) ----------

    # --- sizing / layout ---
    def fluid(self):
        """100% width, keep intrinsic ratio."""
        self._add_runtime("block", "w-[100%]", "h-[auto]")
        return self

    def w(self, v: int | str):
        self._add_runtime(f"w-[{v if isinstance(v, str) else str(v)+'px'}]")
        return self

    def h(self, v: int | str):
        self._add_runtime(f"h-[{v if isinstance(v, str) else str(v)+'px'}]")
        return self

    def size(self, wv: int | str, hv: int | str):
        return self.w(wv).h(hv)

    # --- shape / decoration ---
    def rounded(self, key: str = "md"):
        """Use your tokened radii: sm|md|lg|xl|2xl|3xl|full."""
        self._add_runtime(f"rounded-{key}")
        return self

    def rounded_full(self):
        self._add_runtime("rounded-full")
        return self

    def radius(self, px: int | str):
        """Arbitrary radius in px/rem/etc."""
        self._add_runtime(f"rounded-[{px if isinstance(px,str) else str(px)+'px'}]")
        return self

    def border(self, *, color: str = "subtle", width: int | None = None, style: str = "solid"):
        """
        color: DZN color token, theme scale (e.g., 'accent-500'), or CSS name via border-[...]
        width: 0 | 2 | 4 | 8 (uses your width scale); omit for DEFAULT
        style: solid|dashed|dotted
        """
        parts = ["border"]
        if width in (0, 2, 4, 8):
            parts.append(f"border-{width}")
        parts.append(f"border-{style}")          # border-solid/dashed/dotted
        parts.append(f"border-{color}")          # border-accent-500 or border-subtle etc.
        self._add_runtime(*parts)
        return self

    def shadow(self, level: str = "sm"):
        """level: none|sm|md|lg|xl|2xl|3xl|inner (matches your DZN)."""
        lvl = "shadow" if level == "md" else f"shadow-{level}" if level != "md" else "shadow"
        self._add_runtime(lvl)
        return self

    # --- object-fit / position (inline styles; reliable everywhere) ---
    def fit(self, mode: str = "cover"):
        """mode: cover|contain|fill|none|scale-down."""
        self._append_style(f"object-fit:{mode};")
        return self

    def cover(self):   return self.fit("cover")
    def contain(self): return self.fit("contain")

    def object_position(self, x: str = "50%", y: str = "50%"):
        self._append_style(f"object-position:{x} {y};")
        return self

    def center(self):
        """Convenience: center crop subject."""
        return self.object_position("50%", "50%")

    def top(self):      return self.object_position("50%", "0%")
    def bottom(self):   return self.object_position("50%", "100%")
    def left(self):     return self.object_position("0%",  "50%")
    def right(self):    return self.object_position("100%","50%")
    def top_left(self): return self.object_position("0%",  "0%")
    def top_right(self):return self.object_position("100%","0%")
    def bot_left(self): return self.object_position("0%",  "100%")
    def bot_right(self):return self.object_position("100%","100%")

    # --- placeholders / backgrounds ---
    def placeholder(self, color: str = "rgba(0,0,0,.04)"):
        """Add a background so empty/slow loads have a surface."""
        self._add_runtime(f"bg-[{color}]")
        return self

    # --- loading / performance / a11y ---
    def lazy(self):           self.html_attrs["loading"] = "lazy"; return self
    def eager(self):          self.html_attrs["loading"] = "eager"; return self
    def decode_async(self):   self.html_attrs["decoding"] = "async"; return self
    def priority(self, level: str = "high"):
        """fetchpriority: high|low|auto"""
        self.html_attrs["fetchpriority"] = level
        return self
    def no_referrer(self):    self.html_attrs["referrerpolicy"] = "no-referrer"; return self
    def crossorigin(self, mode: str = "anonymous"):
        self.html_attrs["crossorigin"] = mode
        return self
    def draggable(self, on: bool = False):
        self.html_attrs["draggable"] = "true" if on else "false"
        return self

    # --- srcset / sizes ---
    def src(self, url: str):
        self.html_attrs["src"] = url
        return self

    def alt(self, text: str):
        self.html_attrs["alt"] = text
        return self

    def srcset(self, sources: dict | list[tuple[str, str]] | str):
        """
        sources:
          - dict like {"image@1x.jpg": "1x", "image@2x.jpg": "2x"}
          - list of (url, descriptor) tuples, e.g. [("img-480.jpg","480w"), ...]
          - or a raw string "img-480.jpg 480w, img-800.jpg 800w"
        """
        if isinstance(sources, str):
            self.html_attrs["srcset"] = sources
            return self
        if isinstance(sources, dict):
            parts = [f"{u} {d}" for u, d in sources.items()]
        else:
            parts = [f"{u} {d}" for (u, d) in sources]
        self.html_attrs["srcset"] = ", ".join(parts)
        return self

    def sizes(self, value: str):
        """e.g., '(max-width: 640px) 100vw, 50vw'"""
        self.html_attrs["sizes"] = value
        return self

    # --- convenience combos ---
    def as_avatar(self, size: int = 40):
        """Rounded circle avatar with crop and soft border."""
        return (
            self.w(size).h(size)
                .rounded_full()
                .border(color="subtle", width=1 if size < 40 else 2, style="solid")
                .shadow("sm")
                .cover().center()
        )

    def as_card_media(self, height: int = 200):
        """Full-width media area with crop fill."""
        return self.fluid().h(height).rounded("md").shadow("sm").cover().center()

    # required by BaseComponent
    def context(self) -> dict:
        # No template vars needed; BaseComponent will render attributes
        return {}
