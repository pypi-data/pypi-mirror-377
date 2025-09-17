from pydzn.base_component import BaseComponent
from pydzn.htmx import HtmxSupport
from pydzn.dzn import register_dzn_classes


class LabeledInput(BaseComponent, HtmxSupport):
    """
    <label> + <input> with dzn-aware classes.
    - Uses BaseComponent so it renders from template.html next to this file.
    - label 'for' is wired to the input id.
    - Pass dzn_* to style wrapper/label/input/hint/error with your semantic utilities.
    """

    template_name = "template.html"

    def __init__(
        self,
        *,
        label: str,
        name: str,
        type_: str = "text",
        value: str = "",
        placeholder: str = "",
        autocomplete: str = "",
        required: bool = True,
        disabled: bool = False,
        readonly: bool = False,

        # dzn classes
        dzn: str = "",
        dzn_label: str = "block mb-2",
        dzn_input: str = "block w-full px-4 py-2 rounded-md border border-subtle",
        dzn_hint: str = "text-muted mt-1",
        dzn_error: str = "text-[red] mt-1",

        # optional helper text & error text
        hint: str = "",
        error: str = "",

        # extra attributes for the <input> element only
        input_attrs: dict | None = None,

        # Optional explicit id for the input (else auto-generated)
        input_id: str | None = None,

        **wrapper_attrs,  # goes on the outer wrapper <div>
    ):
        super().__init__(children="", tag="div", dzn=dzn, **wrapper_attrs)

        # Store props
        self.label = label
        self.name = name
        self.type_ = type_
        self.value = value
        self.placeholder = placeholder
        self.autocomplete = autocomplete
        self.required = bool(required)
        self.disabled = bool(disabled)
        self.readonly = bool(readonly)

        self.dzn_label = dzn_label or ""
        self.dzn_input = dzn_input or ""
        self.dzn_hint  = dzn_hint or ""
        self.dzn_error = dzn_error or ""

        self.hint  = hint or ""
        self.error = error or ""

        self.input_attrs = dict(input_attrs or {})
        self.input_id = input_id or (self.id + "-input")

        # Make sure dzn tokens are emitted in /_dzn.css
        register_dzn_classes(" ".join(
            c for c in [self.dzn_label, self.dzn_input, self.dzn_hint, self.dzn_error] if c
        ))

    def context(self) -> dict:
        return {
            "input_id": self.input_id,
            "label": self.label,
            "name": self.name,
            "type_": self.type_,
            "value": self.value,
            "placeholder": self.placeholder,
            "autocomplete": self.autocomplete,
            "required": self.required,
            "disabled": self.disabled,
            "readonly": self.readonly,
            "dzn_label": self.dzn_label,
            "dzn_input": self.dzn_input,
            "dzn_hint": self.dzn_hint,
            "dzn_error": self.dzn_error,
            "hint": self.hint,
            "error": self.error,
            "input_attrs": self.input_attrs,
        }
