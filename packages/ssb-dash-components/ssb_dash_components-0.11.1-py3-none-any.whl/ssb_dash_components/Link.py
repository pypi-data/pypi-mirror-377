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


class Link(Component):
    """A Link component.
A SSB styled Link with Book as default icon

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- ariaLabel (string; optional)

- className (string; default '')

- href (string; required)

- icon (a list of or a singular dash component, string or number; default <Book size={16} />)

- isExternal (boolean; default False)

- linkType (a value equal to: 'regular', 'profiled', 'header'; optional)

- negative (boolean; default False)

- standAlone (boolean; optional)

- tabIndex (number; optional)

- title (string; optional)"""
    _children_props = ['icon']
    _base_nodes = ['icon', 'children']
    _namespace = 'ssb_dash_components'
    _type = 'Link'


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        ariaLabel: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        href: typing.Optional[str] = None,
        icon: typing.Optional[ComponentType] = None,
        isExternal: typing.Optional[bool] = None,
        linkType: typing.Optional[Literal["regular", "profiled", "header"]] = None,
        negative: typing.Optional[bool] = None,
        tabIndex: typing.Optional[NumberType] = None,
        title: typing.Optional[str] = None,
        standAlone: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'ariaLabel', 'className', 'href', 'icon', 'isExternal', 'linkType', 'negative', 'standAlone', 'tabIndex', 'title']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'ariaLabel', 'className', 'href', 'icon', 'isExternal', 'linkType', 'negative', 'standAlone', 'tabIndex', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['href']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Link, self).__init__(children=children, **args)

setattr(Link, "__init__", _explicitize_args(Link.__init__))
