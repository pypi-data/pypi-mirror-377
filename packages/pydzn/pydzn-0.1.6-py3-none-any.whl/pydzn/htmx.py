from __future__ import annotations
from typing import Any, Mapping, Optional, Iterable
import json


def _to_bool(v: Optional[bool]) -> Optional[str]:
    if v is None:
        return None
    return "true" if v else "false"


def _to_params(val: Optional[Iterable[str] | str]) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, str):
        return val
    return ",".join(val)


class HtmxSupport:
    """
    Mixin that adds ergonomic HTMX methods to component classes.

    - Chainable (each method returns self)
    - Safe to call before BaseComponent.__init__: attributes are buffered and
      merged right before render.
    - If self.html_attrs exists, attrs are applied immediately.
    """

    # ---- plumbing ---------------------------------------------------------

    def _hx_store(self, name: str, value: Optional[str], *, override: bool = True) -> "HtmxSupport":
        # lazy init buffer
        if not hasattr(self, "_hx_pending"):
            self._hx_pending: dict[str, str] = {}

        if value is None:
            # remove request to set this attr
            if hasattr(self, "html_attrs") and override:
                self.html_attrs.pop(name, None)  # type: ignore[attr-defined]
            self._hx_pending.pop(name, None)
            return self

        # apply now if html_attrs exists, else buffer
        if hasattr(self, "html_attrs"):
            if override or name not in self.html_attrs:  # type: ignore[attr-defined]
                self.html_attrs[name] = value           # type: ignore[attr-defined]
        else:
            if override or name not in self._hx_pending:
                self._hx_pending[name] = value
        return self

    def _htmx_attrs_as_dict(self) -> dict[str, str]:
        """Called by BaseComponent.render (see tiny patch below)."""
        return dict(getattr(self, "_hx_pending", {}))

    # ---- verbs (requests) -------------------------------------------------

    def hx_get(self, url: str) -> "HtmxSupport":
        return self._hx_store("hx-get", url)

    def hx_post(self, url: str) -> "HtmxSupport":
        return self._hx_store("hx-post", url)

    def hx_put(self, url: str) -> "HtmxSupport":
        return self._hx_store("hx-put", url)

    def hx_patch(self, url: str) -> "HtmxSupport":
        return self._hx_store("hx-patch", url)

    def hx_delete(self, url: str) -> "HtmxSupport":
        return self._hx_store("hx-delete", url)

    # ---- target, swap, url/history ---------------------------------------

    def hx_target(self, selector: str) -> "HtmxSupport":
        return self._hx_store("hx-target", selector)

    def hx_swap(
        self,
        mode: str = "innerHTML",
        *,
        swap: Optional[str] = None,       # e.g. "1s"
        settle: Optional[str] = None,     # e.g. "200ms"
        scroll: Optional[str] = None,     # e.g. "top" or "#id"
        show: Optional[str] = None,       # e.g. "#id"
        focus_scroll: Optional[bool] = None,
        ignore_title: Optional[bool] = None,
    ) -> "HtmxSupport":
        parts: list[str] = [mode]
        if swap:         parts.append(f"swap:{swap}")
        if settle:       parts.append(f"settle:{settle}")
        if scroll:       parts.append(f"scroll:{scroll}")
        if show:         parts.append(f"show:{show}")
        if focus_scroll is not None: parts.append(f"focus-scroll:{_to_bool(focus_scroll)}")
        if ignore_title is not None: parts.append(f"ignoreTitle:{_to_bool(ignore_title)}")
        return self._hx_store("hx-swap", " ".join(parts))

    def hx_push_url(self, value: bool | str = True) -> "HtmxSupport":
        return self._hx_store("hx-push-url", value if isinstance(value, str) else _to_bool(value))

    def hx_replace_url(self, value: bool | str = True) -> "HtmxSupport":
        return self._hx_store("hx-replace-url", value if isinstance(value, str) else _to_bool(value))

    def hx_history(self, enabled: bool) -> "HtmxSupport":
        # controls snapshotting in some setups; false disables history for this elt
        return self._hx_store("hx-history", _to_bool(enabled))

    def hx_history_elt(self, enabled: bool = True) -> "HtmxSupport":
        return self._hx_store("hx-history-elt", _to_bool(enabled))

    # ---- payload & headers ------------------------------------------------

    def hx_vals(self, mapping: Mapping[str, Any]) -> "HtmxSupport":
        return self._hx_store("hx-vals", json.dumps(mapping, separators=(",", ":")))

    def hx_headers(self, mapping: Mapping[str, Any]) -> "HtmxSupport":
        return self._hx_store("hx-headers", json.dumps(mapping, separators=(",", ":")))

    def hx_include(self, selector_or_list: str | Iterable[str]) -> "HtmxSupport":
        if isinstance(selector_or_list, str):
            return self._hx_store("hx-include", selector_or_list)
        return self._hx_store("hx-include", ",".join(selector_or_list))

    def hx_params(self, params: Iterable[str] | str) -> "HtmxSupport":
        """
        Accepts:
          - "none"
          - "not some,other"
          - "a,b,c" (only)
        """
        return self._hx_store("hx-params", _to_params(params))

    def hx_encoding(self, enctype: str) -> "HtmxSupport":
        # e.g., "multipart/form-data" for file uploads
        return self._hx_store("hx-encoding", enctype)

    def hx_sync(self, selector: str, strategy: str = "drop") -> "HtmxSupport":
        # strategy: "drop" | "abort" | "replace" | "queue"
        return self._hx_store("hx-sync", f"{selector}:{strategy}")

    # ---- triggers & events ------------------------------------------------

    def hx_trigger(
        self,
        trigger: Optional[str] = None,
        *,
        event: Optional[str] = None,   # e.g., "click", "change", "revealed"
        changed: bool = False,
        once: bool = False,
        delay: Optional[str] = None,   # "500ms"
        throttle: Optional[str] = None,# "300ms"
        from_: Optional[str] = None,   # ".selector"
        target: Optional[str] = None,  # ".selector"
        consume: bool = False,
        queue: Optional[str] = None,   # "first" | "last" | "all" | "none"
    ) -> "HtmxSupport":
        if trigger:
            return self._hx_store("hx-trigger", trigger)

        ev = event or "click"
        parts: list[str] = [ev]
        if changed:   parts.append("changed")
        if once:      parts.append("once")
        if delay:     parts.append(f"delay:{delay}")
        if throttle:  parts.append(f"throttle:{throttle}")
        if from_:     parts.append(f"from:{from_}")
        if target:    parts.append(f"target:{target}")
        if consume:   parts.append("consume")
        if queue:     parts.append(f"queue:{queue}")
        return self._hx_store("hx-trigger", " ".join(parts))

    def hx_on(self, event: str, js: str) -> "HtmxSupport":
        # emits attribute like: hx-on:click="..." (multiple calls allowed)
        return self._hx_store(f"hx-on:{event}", js)

    # ---- UX, indicators, disable -----------------------------------------

    def hx_indicator(self, selector: str) -> "HtmxSupport":
        return self._hx_store("hx-indicator", selector)

    def hx_confirm(self, text: str) -> "HtmxSupport":
        return self._hx_store("hx-confirm", text)

    def hx_prompt(self, text: str) -> "HtmxSupport":
        return self._hx_store("hx-prompt", text)

    def hx_disabled_elt(self, selector: str) -> "HtmxSupport":
        return self._hx_store("hx-disabled-elt", selector)

    # ---- extensions & transports -----------------------------------------

    def hx_ext(self, ext_names: str) -> "HtmxSupport":
        # e.g., "json-enc" or "ws" or "sse,push-url"
        return self._hx_store("hx-ext", ext_names)

    def hx_ws(self, value: str) -> "HtmxSupport":
        # e.g., "connect:/ws/room-1"
        return self._hx_store("hx-ws", value)

    def hx_sse(self, value: str) -> "HtmxSupport":
        # e.g., "connect:/sse/stream"
        return self._hx_store("hx-sse", value)

    # ---- convenience ------------------------------------------------------

    def hx_boost(self, enabled: bool = True) -> "HtmxSupport":
        return self._hx_store("hx-boost", _to_bool(enabled))

    def hx_select(self, selector: str) -> "HtmxSupport":
        # select a fragment from the response to swap
        return self._hx_store("hx-select", selector)

    def hx_select_oob(self, selector: str) -> "HtmxSupport":
        # apply an out-of-band fragment from the response; often used on response elts
        return self._hx_store("hx-select-oob", selector)

    def hx_clear(self, *names: str) -> "HtmxSupport":
        """Remove one or many hx-* attributes."""
        if not hasattr(self, "_hx_pending"):
            self._hx_pending = {}
        for n in names:
            # remove from both places
            self._hx_pending.pop(n, None)
            if hasattr(self, "html_attrs"):
                self.html_attrs.pop(n, None)  # type: ignore[attr-defined]
        return self

    @property
    def hx_attrs(self) -> dict[str, str]:
        """Introspect current HTMX attrs (buffered + applied)."""
        buf = dict(getattr(self, "_hx_pending", {}))
        if hasattr(self, "html_attrs"):
            for k, v in self.html_attrs.items():   # type: ignore[attr-defined]
                if k.startswith("hx-") or k.startswith("hx-on:"):
                    buf[k] = v
        return buf

    # ---- navigation ----- #
    def hx_navigate(self, url: str, *, replace: bool = False) -> "HtmxSupport":
        """
        Plain full-page navigation on click (no AJAX).
        Uses window.location.assign()/replace().
        """
        fn = "replace" if replace else "assign"
        return self.hx_on("click", f"window.location.{fn}('{url}');")

    def hx_get_page(self, url: str, *, target: str = "body", push_url: bool = True) -> "HtmxSupport":
        """
        SPA-style: fetch URL via htmx and replace a container (default: <body>).
        """
        self.hx_get(url).hx_target(target).hx_swap("outerHTML")
        if push_url:
            self.hx_push_url(True)
        return self

    def hx_redirect_via(self, ping_url: str) -> "HtmxSupport":
        """
        AJAX ping to server; server replies with HX-Redirect/HX-Location.
        Useful when navigation depends on server logic.
        """
        return self.hx_get(ping_url)
