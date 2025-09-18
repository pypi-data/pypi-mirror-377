# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class Input(Component):
    """An Input component.
SSB styled Input field and search field

Keyword arguments:

- id (string; optional)

- ariaLabel (string; optional)

- ariaLabelSearchButton (string; default 'search')

- ariaLabelWrapper (string; optional)

- ariaLabelledBy (string; optional)

- className (string; default '')

- debounce (boolean; default False):
    If this is set to True, then values will only be sent when Enter
    is pressed or focus is lost.

- description (string; optional):
    Add explanation text.

- disabled (boolean; default False)

- error (boolean; default False)

- errorMessage (string; optional)

- label (string; optional)

- n_submit (number; optional)

- name (string; optional)

- negative (boolean; default False)

- placeholder (string; optional)

- readOnly (boolean; default False):
    Use this attribute on non editable input fields.

- required (boolean; default False):
    Add a red asterisk after the label to indicate to an end user that
    the input must be filled out.

- role (string; optional)

- searchField (boolean; default False)

- showDescription (boolean; optional):
    Set True to show description.

- size (string; optional)

- type (string; default 'text')

- value (string; default '')"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'Input'


    def __init__(
        self,
        role: typing.Optional[str] = None,
        ariaLabelWrapper: typing.Optional[str] = None,
        ariaLabel: typing.Optional[str] = None,
        ariaLabelledBy: typing.Optional[str] = None,
        ariaLabelSearchButton: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        disabled: typing.Optional[bool] = None,
        error: typing.Optional[bool] = None,
        errorMessage: typing.Optional[str] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        label: typing.Optional[str] = None,
        negative: typing.Optional[bool] = None,
        placeholder: typing.Optional[str] = None,
        searchField: typing.Optional[bool] = None,
        size: typing.Optional[str] = None,
        type: typing.Optional[str] = None,
        value: typing.Optional[str] = None,
        n_submit: typing.Optional[NumberType] = None,
        showDescription: typing.Optional[bool] = None,
        description: typing.Optional[str] = None,
        readOnly: typing.Optional[bool] = None,
        debounce: typing.Optional[bool] = None,
        required: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'ariaLabel', 'ariaLabelSearchButton', 'ariaLabelWrapper', 'ariaLabelledBy', 'className', 'debounce', 'description', 'disabled', 'error', 'errorMessage', 'label', 'n_submit', 'name', 'negative', 'placeholder', 'readOnly', 'required', 'role', 'searchField', 'showDescription', 'size', 'type', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'ariaLabel', 'ariaLabelSearchButton', 'ariaLabelWrapper', 'ariaLabelledBy', 'className', 'debounce', 'description', 'disabled', 'error', 'errorMessage', 'label', 'n_submit', 'name', 'negative', 'placeholder', 'readOnly', 'required', 'role', 'searchField', 'showDescription', 'size', 'type', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Input, self).__init__(**args)

setattr(Input, "__init__", _explicitize_args(Input.__init__))
