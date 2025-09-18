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


class Button(Component):
    """A Button component.
SSB styled Button for triggering actions

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Button text or/and icon.

- id (string; optional)

- ariaLabel (string; default '')

- className (string; default ''):
    Optional container class.

- disabled (boolean; default False):
    Decides if the button is disabled.

- icon (a list of or a singular dash component, string or number; optional):
    Renders an icon.

- n_clicks (number; default 0):
    Number of times the button has been clicked.

- negative (boolean; default False):
    Changes design.

- primary (boolean; default False):
    Changes style to represent a primary button.

- type (string; default 'button'):
    Button type. Can be 'submit', 'reset', or 'button'. Defaults to
    'button'."""
    _children_props = ['icon']
    _base_nodes = ['icon', 'children']
    _namespace = 'ssb_dash_components'
    _type = 'Button'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        n_clicks: typing.Optional[NumberType] = None,
        className: typing.Optional[str] = None,
        disabled: typing.Optional[bool] = None,
        icon: typing.Optional[ComponentType] = None,
        negative: typing.Optional[bool] = None,
        primary: typing.Optional[bool] = None,
        type: typing.Optional[str] = None,
        ariaLabel: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'ariaLabel', 'className', 'disabled', 'icon', 'n_clicks', 'negative', 'primary', 'type']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'ariaLabel', 'className', 'disabled', 'icon', 'n_clicks', 'negative', 'primary', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Button, self).__init__(children=children, **args)

setattr(Button, "__init__", _explicitize_args(Button.__init__))
