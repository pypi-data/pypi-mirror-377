from __future__ import annotations
from typing import ClassVar, Dict, Iterable, Mapping, Optional
from pydzn.dzn import register_dzn_classes


class VariantSupport:
    """
    Mixin for components that want tailwind-like 'variant/size/tone' presets
    with pluggable, namespaced libraries.

    Subclasses typically define:
      VARIANTS: Mapping[str, str]
      SIZES:    Mapping[str, str]
      TONES:    Mapping[str, str]
      DEFAULTS: Mapping[str, str]  # e.g. {"variant":"outline-primary", "size":"md", "tone":""}

    Public API on each component class:
      - attach_variant_library(namespace, variants=..., sizes=..., tones=..., override=False)
      - set_default_choices(variant=..., size=..., tone=...)
      - list_variants(namespaced=True) -> list[str]
      - list_sizes(namespaced=True) -> list[str]
      - list_tones(namespaced=True) -> list[str]
      - available_options(namespaced=True) -> dict with "variants"/"sizes"/"tones"/"defaults"

    Instance-side helper used by __init__ of the component:
      - _resolve_variant_dzn(variant, size, tone, extra_dzn) -> str
    """

    # Per-subclass external libs: { "ns": {"variants":{...}, "sizes":{...}, "tones":{...}} }
    _external_libs: ClassVar[Dict[str, Dict[str, Dict[str, str]]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # init per-class registry
        if not hasattr(cls, "_external_libs"):
            cls._external_libs = {}
        # sane fallbacks so list_* never explode
        for attr, default in (("VARIANTS", {}), ("SIZES", {}), ("TONES", {}), ("DEFAULTS", {})):
            if not hasattr(cls, attr):
                setattr(cls, attr, default)

    # ---------- library plumbing ----------

    @classmethod
    def attach_variant_library(
        cls,
        namespace: str,
        *,
        variants: Optional[Mapping[str, str]] = None,
        sizes: Optional[Mapping[str, str]] = None,
        tones: Optional[Mapping[str, str]] = None,
        override: bool = False,
    ) -> None:
        """
        Attach or extend a namespaced library for this component class only.
        Example:
            Button.attach_variant_library(
                "acme",
                variants={"glass": "px-5 py-2 rounded-md bg-[rgba(...", ...},
                sizes={"xl": "px-7 py-4"},
                tones={"success": "bg-[..."}
            )
        """
        ns = namespace.strip()
        if not ns:
            raise ValueError("attach_variant_library: namespace cannot be empty")

        lib = cls._external_libs.get(ns, {"variants": {}, "sizes": {}, "tones": {}})
        if override:
            lib = {
                "variants": dict(variants or {}),
                "sizes": dict(sizes or {}),
                "tones": dict(tones or {}),
            }
        else:
            if variants:
                lib["variants"].update(variants)
            if sizes:
                lib["sizes"].update(sizes)
            if tones:
                lib["tones"].update(tones)

        cls._external_libs[ns] = lib

        # Register DZN so emitted CSS includes these utilities
        all_classes: list[str] = []
        for m in (variants or {}).values():
            all_classes.append(m)
        for m in (sizes or {}).values():
            all_classes.append(m)
        for m in (tones or {}).values():
            all_classes.append(m)
        if all_classes:
            register_dzn_classes(" ".join(all_classes))

    @classmethod
    def set_default_choices(
        cls,
        *,
        variant: Optional[str] = None,
        size: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> None:
        d = dict(getattr(cls, "DEFAULTS", {}))
        if variant is not None:
            d["variant"] = variant
        if size is not None:
            d["size"] = size
        if tone is not None:
            d["tone"] = tone
        cls.DEFAULTS = d

    # ---------- listing helpers (what you asked for) ----------

    @classmethod
    def list_variants(cls, *, namespaced: bool = True) -> list[str]:
        """
        Return all available variant keys.
        If namespaced=True, external libs appear as 'ns:key'.
        """
        keys: list[str] = list(getattr(cls, "VARIANTS", {}).keys())
        if namespaced:
            for ns, lib in cls._external_libs.items():
                keys.extend([f"{ns}:{k}" for k in lib.get("variants", {}).keys()])
        else:
            # note: non-namespaced duplicates could collide; this is just the names
            for lib in cls._external_libs.values():
                keys.extend(lib.get("variants", {}).keys())
        return sorted(keys)

    @classmethod
    def list_sizes(cls, *, namespaced: bool = True) -> list[str]:
        keys: list[str] = list(getattr(cls, "SIZES", {}).keys())
        if namespaced:
            for ns, lib in cls._external_libs.items():
                keys.extend([f"{ns}:{k}" for k in lib.get("sizes", {}).keys()])
        else:
            for lib in cls._external_libs.values():
                keys.extend(lib.get("sizes", {}).keys())
        return sorted(set(keys))

    @classmethod
    def list_tones(cls, *, namespaced: bool = True) -> list[str]:
        keys: list[str] = list(getattr(cls, "TONES", {}).keys())
        if namespaced:
            for ns, lib in cls._external_libs.items():
                keys.extend([f"{ns}:{k}" for k in lib.get("tones", {}).keys()])
        else:
            for lib in cls._external_libs.values():
                keys.extend(lib.get("tones", {}).keys())
        return sorted(set(keys))

    @classmethod
    def available_options(cls, *, namespaced: bool = True) -> dict:
        """
        Structured view for UIs: { variants: [...], sizes: [...], tones: [...], defaults: {...} }
        """
        return {
            "variants": cls.list_variants(namespaced=namespaced),
            "sizes": cls.list_sizes(namespaced=namespaced),
            "tones": cls.list_tones(namespaced=namespaced),
            "defaults": dict(getattr(cls, "DEFAULTS", {})),
        }

    # ---------- resolution used by your component __init__ ----------

    @classmethod
    def _lookup_variant_piece(cls, kind: str, key: Optional[str]) -> str:
        """
        kind = 'variants' | 'sizes' | 'tones'
        key may be namespaced 'ns:name'. Returns DZN string or ''.
        """
        if not key:
            return ""

        # external: ns:key
        if ":" in key:
            ns, name = key.split(":", 1)
            lib = cls._external_libs.get(ns, {})
            return lib.get(kind, {}).get(name, "")

        # built-in
        table = getattr(cls, kind.upper(), {})
        return table.get(key, "")

    def _resolve_variant_dzn(
        self,
        *,
        variant: Optional[str],
        size: Optional[str],
        tone: Optional[str],
        extra_dzn: Optional[str] = None,
    ) -> str:
        cls = self.__class__
        defaults = getattr(cls, "DEFAULTS", {})

        v_key = variant if variant is not None else defaults.get("variant", "")
        s_key = size    if size    is not None else defaults.get("size", "")
        t_key = tone    if tone    is not None else defaults.get("tone", "")

        parts: list[str] = []
        v = cls._lookup_variant_piece("variants", v_key)
        if v: parts.append(v)
        s = cls._lookup_variant_piece("sizes", s_key)
        if s: parts.append(s)
        t = cls._lookup_variant_piece("tones", t_key)
        if t: parts.append(t)
        if extra_dzn:
            parts.append(extra_dzn)
        resolved = " ".join(p for p in parts if p).strip()

        # register resolved classes once more (cheap) so /_dzn.css emits them
        if resolved:
            register_dzn_classes(resolved)
        return resolved
