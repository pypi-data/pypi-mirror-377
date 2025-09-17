from pydzn.base_component import BaseComponent
from pydzn.htmx import HtmxSupport


class Form(BaseComponent, HtmxSupport):
    """
    Minimal <form> that supports dzn classes and HTMX attributes.
    """
    template_name = "template.html"

    def __init__(self, children: str = "", *, action: str = "", method: str = "post",
                 dzn: str = "", **attrs):
        # default progressive enhancement: real form action/method + HTMX attrs
        attrs.setdefault("action", action)
        attrs.setdefault("method", method.lower())
        super().__init__(children=children, tag="form", dzn=dzn, **attrs)

    def context(self) -> dict:
        return {}
