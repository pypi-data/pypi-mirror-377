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


class InputError(Component):
    """An InputError component.


Keyword arguments:

- id (string; optional)

- className (string; optional)

- errorMessage (string; required)

- negative (boolean; default False)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'InputError'


    def __init__(
        self,
        className: typing.Optional[str] = None,
        errorMessage: typing.Optional[str] = None,
        negative: typing.Optional[bool] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'className', 'errorMessage', 'negative']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'errorMessage', 'negative']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['errorMessage']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(InputError, self).__init__(**args)

setattr(InputError, "__init__", _explicitize_args(InputError.__init__))
