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


class Header(Component):
    """A Header component.
SSB styled Header component.
A wrapper for displaying a header

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    All rendered content.

- className (string; optional):
    Optional container class."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'Header'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        className: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'className']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'className']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Header, self).__init__(children=children, **args)

setattr(Header, "__init__", _explicitize_args(Header.__init__))
