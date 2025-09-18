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


class Accordion(Component):
    """An Accordion component.
A SSB styled expandable accordion

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Accordion content.

- id (string; optional):
    Optional id.

- className (string; optional):
    Optional container class.

- header (string; optional):
    Header text.

- openByDefault (boolean; optional):
    Will set the open state on init.

- subHeader (string; optional):
    Renders the header with the sub header design.

- tabIndex (number; optional):
    Makes tab elements focusable.

- withoutBorders (boolean; optional):
    Default False, Accordion without border on top and bottom if value
    is True."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'Accordion'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[str] = None,
        header: typing.Optional[str] = None,
        openByDefault: typing.Optional[bool] = None,
        subHeader: typing.Optional[str] = None,
        tabIndex: typing.Optional[NumberType] = None,
        withoutBorders: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'className', 'header', 'openByDefault', 'subHeader', 'tabIndex', 'withoutBorders']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'header', 'openByDefault', 'subHeader', 'tabIndex', 'withoutBorders']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Accordion, self).__init__(children=children, **args)

setattr(Accordion, "__init__", _explicitize_args(Accordion.__init__))
