from __future__ import annotations
from typing import List, Dict, Any, Optional, Iterable
from pydzn.base_component import BaseComponent
from pydzn.variants import VariantSupport
from pydzn.htmx import HtmxSupport
from pydzn.dzn import register_dzn_classes


class Table(VariantSupport, BaseComponent, HtmxSupport):
    """
    Server-rendered Table with:
      - arbitrary columns/rows
      - sortable headers (HTMX)
      - optional toolbar (Export / Add Column)
      - row striping
      - variants/sizes/tones

    Columns: list of dicts like:
      { "key": "id", "label": "ID", "sortable": True, "width": "80px", "align": "left", "dzn": "..." }

    Rows: list[dict], keys match column["key"]. Values can be strings (HTML allowed) or already-rendered HTML.
    """

    template_name = "template.html"

    VARIANTS = {
        # container look
        "surface":  "flex flex-col gap-2 rounded-lg border border-subtle bg-[white] shadow-sm p-0",
        "minimal":  "flex flex-col gap-2 rounded-md border-0 bg-[transparent] shadow-none p-0",
        "soft":     "flex flex-col gap-2 rounded-lg border border-subtle bg-[rgba(15,23,42,.03)] shadow-sm p-0",
        "outlined": "flex flex-col gap-2 rounded-lg border-2 border-slate-300 bg-[transparent] shadow-none p-0",
    }

    # affects cell padding density (used in template via context)
    SIZES = {
        "sm": "px-3 py-2",
        "md": "px-4 py-3",
        "lg": "px-5 py-4",
    }

    # tones to tweak border/header emphasis
    TONES = {
        "neutral": "border-subtle",
        "primary": "border-blue-500",
        "danger":  "border-red-500",
        "success": "border-green-500",
    }

    DEFAULTS = {
        "variant": "surface",
        "size": "md",
        "tone": "neutral",
    }

    def __init__(
        self,
        *,
        columns: List[Dict[str, Any]],
        rows: List[Dict[str, Any]],
        sort_url: Optional[str] = None,      # endpoint to hit for sorting (returns full table HTML)
        sort_key: Optional[str] = None,      # current sort column key
        sort_dir: str = "asc",               # "asc" | "desc"
        export_url: Optional[str] = None,    # if set, toolbar shows Export (plain navigation)
        add_column_url: Optional[str] = None,# if set, toolbar shows Add Column (hx-get to this)
        show_toolbar: bool = False,
        striped: bool = False,               # alternate row background
        # variant system
        variant: Optional[str] = None,
        size: Optional[str] = None,
        tone: Optional[str] = None,
        # raw utility escape hatch (merged last)
        dzn: Optional[str] = None,
        **attrs,
    ):
        self.columns = columns or []
        self.rows = rows or []
        self.sort_url = sort_url
        self.sort_key = sort_key
        self.sort_dir = "desc" if str(sort_dir).lower() == "desc" else "asc"
        self.export_url = export_url
        self.add_column_url = add_column_url
        self.show_toolbar = bool(show_toolbar or export_url or add_column_url)
        self.striped = bool(striped)

        # Resolve variant/size/tone and capture size padding for cells
        size_key = size if size is not None else self.DEFAULTS.get("size", "md")
        # size dzn to apply on each <td>/<th>
        self._cell_pad_dzn = self.__class__._lookup_variant_piece("sizes", size_key) or "px-4 py-3"

        effective_dzn = self._resolve_variant_dzn(
            variant=variant,
            size=size,
            tone=tone,
            extra_dzn=dzn or attrs.pop("dzn", None),
        )

        # Register internal classes used inside template so /_dzn.css emits them
        register_dzn_classes(
            " ".join([
                "w-[100%]",
                "border-b", "border-t", "border-l", "border-r",
                "border-subtle", "text-left", "text-center", "text-right",
                "hover:bg-[rgba(15,23,42,.04)]",
                "bg-[rgba(15,23,42,.03)]",
                self._cell_pad_dzn,
                "px-2 py-1 px-3 py-2 px-4 py-3 px-5 py-4",  # ensure all densities exist in CSS
                "rounded-sm border bg-[white] text-[black]",
            ])
        )

        super().__init__(children="", tag="div", dzn=effective_dzn, **attrs)

    # Jinja context
    def context(self) -> dict:
        return {
            "id": self.id,
            "columns": self.columns,
            "rows": self.rows,
            "sort_url": self.sort_url,
            "sort_key": self.sort_key,
            "sort_dir": self.sort_dir,
            "toggle_dir": "desc" if self.sort_dir == "asc" else "asc",
            "cell_pad_dzn": self._cell_pad_dzn,
            "show_toolbar": self.show_toolbar,
            "export_url": self.export_url,
            "add_column_url": self.add_column_url,
            "striped": self.striped,
        }
