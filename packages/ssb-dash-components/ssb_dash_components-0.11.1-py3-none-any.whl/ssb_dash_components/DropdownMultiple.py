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


class DropdownMultiple(Component):
    """A DropdownMultiple component.


Keyword arguments:

- id (string; optional)

- ariaLabel (string; optional)

- className (string; optional)

- description (string; optional):
    Add explanation text.

- error (boolean; optional)

- errorMessage (string; optional)

- header (string; default '')

- icon (dict; optional)

- items (list of dicts; default [{ id: '', title: '' }])

    `items` is a list of dicts with keys:

    - title (string; optional)

    - id (string; optional)

    - disabled (boolean; optional)

- largeSize (boolean; optional)

- open (boolean; default False)

- placeholder (string; default '-- Select --')

- searchable (boolean; default False)

- showDescription (boolean; optional):
    Set True to show glossary.

- tabIndex (number; optional)

- value (list; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'DropdownMultiple'
    Items = TypedDict(
        "Items",
            {
            "title": NotRequired[str],
            "id": NotRequired[str],
            "disabled": NotRequired[bool]
        }
    )


    def __init__(
        self,
        ariaLabel: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        error: typing.Optional[bool] = None,
        errorMessage: typing.Optional[str] = None,
        header: typing.Optional[str] = None,
        icon: typing.Optional[dict] = None,
        items: typing.Optional[typing.Sequence["Items"]] = None,
        open: typing.Optional[bool] = None,
        placeholder: typing.Optional[str] = None,
        searchable: typing.Optional[bool] = None,
        tabIndex: typing.Optional[NumberType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        largeSize: typing.Optional[bool] = None,
        value: typing.Optional[typing.Sequence] = None,
        showDescription: typing.Optional[bool] = None,
        description: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'ariaLabel', 'className', 'description', 'error', 'errorMessage', 'header', 'icon', 'items', 'largeSize', 'open', 'placeholder', 'searchable', 'showDescription', 'tabIndex', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'ariaLabel', 'className', 'description', 'error', 'errorMessage', 'header', 'icon', 'items', 'largeSize', 'open', 'placeholder', 'searchable', 'showDescription', 'tabIndex', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DropdownMultiple, self).__init__(**args)

setattr(DropdownMultiple, "__init__", _explicitize_args(DropdownMultiple.__init__))
