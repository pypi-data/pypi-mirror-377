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


class Title(Component):
    """A Title component.
TitleComponent is a SSB component handling header elements.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; optional)

- className (string; optional)

- negative (boolean; optional):
    Toggles text color.

- size (a value equal to: 1, 2, 3, 4, 5, 6; optional):
    Change header element size according to rules for Heading ranks."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'Title'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        className: typing.Optional[str] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        negative: typing.Optional[bool] = None,
        size: typing.Optional[Literal[1, 2, 3, 4, 5, 6]] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'className', 'negative', 'size']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'negative', 'size']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Title, self).__init__(children=children, **args)

setattr(Title, "__init__", _explicitize_args(Title.__init__))
