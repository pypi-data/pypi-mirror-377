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


class Dialog(Component):
    """A Dialog component.
SSB styled dialog component.
A wrapper for displaying a dialog

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    All rendered content.

- id (string; optional)

- className (string; optional):
    Optional container class.

- is_open (boolean; optional)

- title (string; required)

- type (a value equal to: 'info', 'warning'; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'Dialog'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        is_open: typing.Optional[bool] = None,
        title: typing.Optional[str] = None,
        type: typing.Optional[Literal["info", "warning"]] = None,
        className: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'className', 'is_open', 'title', 'type']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'is_open', 'title', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['title']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Dialog, self).__init__(children=children, **args)

setattr(Dialog, "__init__", _explicitize_args(Dialog.__init__))
