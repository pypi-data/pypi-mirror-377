from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
import html
from .dzn import register_dzn_classes


CSSVal = Union[int, str]


def _css_px(v: CSSVal) -> str:
    if isinstance(v, int):
        return f"{v}px"
    return str(v)

def _join_tokens(parts: List[str]) -> str:
    # DZN arbitrary classes use "_" instead of spaces inside [...]
    return "_".join(p.replace(" ", "_") for p in parts)

def _grid_cols_class(named_cols: List[Tuple[str, str]]) -> str:
    return f"grid-cols-[{_join_tokens([w for _, w in named_cols])}]"

def _grid_rows_class(named_rows: List[Tuple[str, str]]) -> str:
    return f"grid-rows-[{_join_tokens([h for _, h in named_rows])}]"

@dataclass
class _Region:
    name: str
    col_name: str
    row_name: Optional[str]           # if None, will resolve to first row
    col_span: Union[int, str] = 1     # NEW: allow "all" -> 1 / -1
    row_span: Optional[int] = 1       # if None => span all rows
    dzn: str = ""

    # placement resolved at build-time (indexes)
    _col_index: int = 1
    _row_index: int = 1
    _row_span_resolved: int = 1

    def placement_style(self) -> str:
        # If col_span is "all", always span first-to-last column; ignore col_name
        if isinstance(self.col_span, str) and self.col_span.lower() == "all":
            gc = "1 / -1"
        else:
            gc = f"{self._col_index} / span {self.col_span}"
        gr = f"{self._row_index} / span {self._row_span_resolved}"
        return f"grid-column:{gc};grid-row:{gr};"

class GridLayoutBuilder:
    """
    Intuitive rows/columns named builder.

    You define tracks by NAME (order preserved), then drop regions by name:

        DashboardLayout = (
            layout_builder()
              .columns(sidebar=280, main="1fr")
              .rows(hero="auto", content="1fr")
              .region("sidebar", col="sidebar", row=None, row_span=None)   # spans all rows
              .region("hero",    col="main",    row="hero")
              .region("content", col="main",    row="content")
              .build(name="DashboardLayout")
        )

    Then use on any page:

        html = DashboardLayout(debug=True).render(
            sidebar=sidebar_html,
            hero=hero_html,
            content=content_html
        )
    """

    def __init__(self):
        self._named_cols: List[Tuple[str, str]] = [("main", "1fr")]
        self._named_rows: List[Tuple[str, str]] = [("content", "1fr")]
        self._regions: List[_Region] = []
        # Defaults that can be overridden per-instance at render() time
        self._default_outer_dzn: str = ""      # wrapper
        self._default_container_dzn: str = ""  # inner grid
        self._height_css: str = "100vh"        # default grid height value
        # NEW: which CSS property to use for height control ("min-height" | "height" | "both")
        self._height_property: str = "min-height"
        self._height_apply_to: str = "container"  # 'outer' | 'container' | 'both'

    # ---------------- optional builder-level defaults ----------------
    def outer_dzn(self, classes: str) -> "GridLayoutBuilder":
        """Set default classes for the OUTER wrapper; can be overridden at render()."""
        self._default_outer_dzn = classes or ""
        return self

    def container_dzn(self, classes: str) -> "GridLayoutBuilder":
        """Set default classes for the INNER grid container; can be overridden at render()."""
        self._default_container_dzn = classes or ""
        return self

    # ---------------- tracks (named & ordered) ----------------
    def columns(self, **spec: CSSVal) -> "GridLayoutBuilder":
        """
        Define columns with names, in the order you pass them:
            .columns(sidebar=280, main="1fr")
        """
        if not spec:
            raise ValueError("columns(): provide at least one named column")
        self._named_cols = [(k, _css_px(v)) for k, v in spec.items()]
        return self

    def rows(self, **spec: CSSVal) -> "GridLayoutBuilder":
        """
        Define rows with names, in the order you pass them:
            .rows(hero="auto", content="1fr")
        """
        if not spec:
            raise ValueError("rows(): provide at least one named row")
        self._named_rows = [(k, _css_px(v)) for k, v in spec.items()]
        return self

    def add_column(self, name: str, width: CSSVal) -> "GridLayoutBuilder":
        self._named_cols.append((name, _css_px(width)))
        return self

    def add_row(self, name: str, height: CSSVal) -> "GridLayoutBuilder":
        self._named_rows.append((name, _css_px(height)))
        return self

    def fill_height(self, css_value: str = "100vh", *, property: str = "min-height", apply_to: str = "container"):
        """
        Control vertical sizing.
          - property: "min-height" | "height" | "both"
          - apply_to: "container" (inner grid), "outer" (outer wrapper), or "both"
        """
        if property not in ("min-height", "height", "both"):
            raise ValueError("fill_height(property=...) must be 'min-height', 'height', or 'both'")
        if apply_to not in ("container", "outer", "both"):
            raise ValueError("fill_height(apply_to=...) must be 'container', 'outer', or 'both'")
        self._height_css = css_value
        self._height_property = property
        self._height_apply_to = apply_to
        return self

    # ---------------- convenience shapes ----------------
    def with_sidebar(self, *, width: CSSVal = 280, position: str = "left") -> "GridLayoutBuilder":
        """
        Quick two-column pattern with sidebar + main.
        Rows untouched; add rows() or add_row() after if you want multiple rows.
        """
        pos = "right" if str(position).lower() == "right" else "left"
        if pos == "left":
            self._named_cols = [("sidebar", _css_px(width)), ("main", "1fr")]
        else:
            self._named_cols = [("main", "1fr"), ("sidebar", _css_px(width))]
        return self

    # ---------------- regions ----------------
    def region(
        self,
        name: str,
        *,
        col: str,
        row: Optional[str],
        col_span: Union[int, str] = 1,   # NEW: accept "all"
        row_span: Optional[int] = 1,     # None = span all rows
        dzn: str = "",
    ) -> "GridLayoutBuilder":
        """
        Add a region by track names. Example:
          .region("sidebar", col="sidebar", row=None, row_span=None)  # full height
          .region("hero",    col="main",    row="hero")
          .region("content", col="main",    row="content")

        Special:
          - col_span="all" → emits grid-column: 1 / -1 (spans every defined column).
            In this mode, the provided `col` is ignored.
        """
        self._regions.append(
            _Region(
                name=name,
                col_name=col,
                row_name=row,
                col_span=col_span,
                row_span=row_span,
                dzn=dzn,
            )
        )
        return self

    # ---------------- build ----------------
    def build(self, *, name: str = "BuiltGridLayout"):
        # Prepare grid class names (optional styling)
        grid_cols = _grid_cols_class(self._named_cols)
        grid_rows = _grid_rows_class(self._named_rows)
        register_dzn_classes([grid_cols, grid_rows])  # let /_dzn.css emit helpers if needed
        register_dzn_classes(["grid"])                # if you have .grid { display:grid } in dzn

        # name→index maps
        col_index: Dict[str, int] = {n: i + 1 for i, (n, _) in enumerate(self._named_cols)}
        row_index: Dict[str, int] = {n: i + 1 for i, (n, _) in enumerate(self._named_rows)}
        total_rows = len(self._named_rows)

        # resolve placements (indices, spans)
        resolved: Dict[str, _Region] = {}
        order: List[str] = []
        for r in self._regions:
            # Only compute a column index if we are NOT spanning all columns
            if not (isinstance(r.col_span, str) and r.col_span.lower() == "all"):
                if r.col_name not in col_index:
                    raise ValueError(f"Unknown column '{r.col_name}' for region '{r.name}'")
                r._col_index = col_index[r.col_name]

            if r.row_name is None:
                r._row_index = 1
                r._row_span_resolved = total_rows if r.row_span is None else r.row_span
            else:
                if r.row_name not in row_index:
                    raise ValueError(f"Unknown row '{r.row_name}' for region '{r.name}'")
                r._row_index = row_index[r.row_name]
                r._row_span_resolved = total_rows - (r._row_index - 1) if r.row_span is None else r.row_span

            resolved[r.name] = r
            order.append(r.name)

        height_css = self._height_css
        height_prop = self._height_property
        height_apply_to = self._height_apply_to

        # capture builder-level defaults into closure
        default_outer_dzn = self._default_outer_dzn
        default_container_dzn = self._default_container_dzn

        # inside build() just before class _Layout:
        class _Layout:
            __slots__ = (
                "_grid_cols", "_grid_rows", "_regions", "_order",
                "_outer_dzn", "_container_dzn", "_region_dzn",
                "_outer_id", "_container_id", "_region_ids", "_debug"
            )

            def __init__(
                self,
                *,
                # alias: `dzn` == outer wrapper classes
                dzn: str = "",
                outer_dzn: str = "",
                container_dzn: str = "",
                region_dzn: Optional[Dict[str, str]] = None,

                # NEW: id hooks
                outer_id: str = "",
                container_id: str = "",
                region_ids: Optional[Dict[str, str]] = None,

                debug: bool = False,
            ):
                self._grid_cols = grid_cols
                self._grid_rows = grid_rows
                self._regions   = resolved
                self._order     = order

                # merge builder defaults + per-instance args (as you already do)
                eff_outer     = " ".join(x for x in [default_outer_dzn, outer_dzn, dzn] if x).strip()
                eff_container = " ".join(x for x in [default_container_dzn, container_dzn] if x).strip()

                self._outer_dzn     = eff_outer
                self._container_dzn = eff_container
                self._region_dzn    = region_dzn or {}

                # NEW: ids
                self._outer_id     = outer_id or ""
                self._container_id = container_id or ""
                self._region_ids   = region_ids or {}

                self._debug = bool(debug)

                if self._outer_dzn:
                    register_dzn_classes(self._outer_dzn)
                if self._container_dzn:
                    register_dzn_classes(self._container_dzn)
                if self._region_dzn:
                    register_dzn_classes(" ".join(self._region_dzn.values()))

            def render(self, **slots: str) -> str:
                # id/class attrs for outer
                outer_id_attr   = f' id="{html.escape(self._outer_id)}"' if self._outer_id else ""
                outer_class_attr= f' class="{html.escape(self._outer_dzn)}"' if self._outer_dzn else ""

                # inner grid class (+ optional id)
                grid_class = " ".join(c for c in ["grid", self._grid_cols, self._grid_rows, self._container_dzn] if c).strip()
                container_id_attr = f' id="{html.escape(self._container_id)}"' if self._container_id else ""

                # height styles (unchanged)
                outer_style_parts: List[str] = []
                grid_style_parts:  List[str] = ["display:grid;"]
                def _apply_height(parts: List[str]):
                    if height_prop == "both":
                        parts.append(f"height:{html.escape(height_css)};")
                        parts.append(f"min-height:{html.escape(height_css)};")
                    elif height_prop == "height":
                        parts.append(f"height:{html.escape(height_css)};")
                    else:
                        parts.append(f"min-height:{html.escape(height_css)};")
                if height_apply_to in ("outer", "both"):
                    _apply_height(outer_style_parts)
                if height_apply_to in ("container", "both"):
                    _apply_height(grid_style_parts)

                outer_style_attr = f' style="{"".join(outer_style_parts)}"' if outer_style_parts else ""
                grid_style_attr  = f' style="{"".join(grid_style_parts)}"'

                out: List[str] = []
                out.append(f"<div{outer_id_attr}{outer_class_attr}{outer_style_attr}>")
                out.append(f'  <div{container_id_attr} class="{html.escape(grid_class)}"{grid_style_attr}>')

                for name in self._order:
                    R = self._regions[name]
                    slot_html = slots.get(name, "") or ""

                    # NEW: optional per-region id
                    rid = self._region_ids.get(name, "")
                    region_id_attr = f' id="{html.escape(rid)}"' if rid else ""

                    region_cls = " ".join(c for c in [R.dzn, self._region_dzn.get(name, "")] if c).strip()
                    region_cls_attr = f' class="{html.escape(region_cls)}"' if region_cls else ""
                    region_style_attr = f' style="{html.escape(R.placement_style())}"'

                    if self._debug:
                        dbg_outline = "outline:1px dashed rgba(220,38,38,.55);outline-offset:-1px;"
                        has_pos = any(tok in (region_cls.split() if region_cls else []) for tok in {"fixed","absolute","relative","sticky"})
                        dbg = dbg_outline + ("" if has_pos else "position:relative;")
                        region_style_attr = region_style_attr[:-1] + dbg + '"'

                    out.append(f'    <div{region_id_attr} data-region="{html.escape(name)}"{region_cls_attr}{region_style_attr}>')
                    if self._debug:
                        out.append(
                            '      <div style="position:absolute;top:2px;left:2px;z-index:1;'
                            'font:11px/1.2 system-ui, -apple-system, Segoe UI, Roboto;'
                            'color:rgba(220,38,38,.8);padding:2px 4px;'
                            'background:rgba(255,255,255,.6);border-radius:3px;pointer-events:none;">'
                            f'{html.escape(name)}</div>'
                        )
                    if slot_html:
                        out.append(f"      {slot_html}")
                    out.append("    </div>")

                out.append("  </div>")
                out.append("</div>")
                return "\n".join(out)


        _Layout.__name__ = name
        return _Layout


def layout_builder() -> GridLayoutBuilder:
    return GridLayoutBuilder()
