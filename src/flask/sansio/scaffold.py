from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union
import os
import pathlib
import sys
import importlib.util
from werkzeug.exceptions import HTTPException, default_exceptions
from flask import Flask, Blueprint, request, jsonify
from flask.views import MethodView

T = TypeVar('T')
ft.RouteCallable = Callable[[Any], Any]
ft.ErrorHandlerCallable = Callable[[HTTPException], Any]

class Scaffold:
    def route(self, rule: str, **options: Any) -> Callable[[ft.RouteCallable], ft.RouteCallable]:
        def decorator(f: ft.RouteCallable) -> ft.RouteCallable:
            endpoint = options.pop('endpoint', None)
            if endpoint is None:
                endpoint = _endpoint_from_view_func(f)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule: str, endpoint: str, view_func: ft.RouteCallable, **options: Any) -> None:
        methods = options.pop('methods', None)
        if methods is not None and 'QUERY' in methods:
            self.add_query_route(rule, endpoint, view_func, **options)
        else:
            super().add_url_rule(rule, endpoint, view_func, **options)

    def add_query_route(self, rule: str, endpoint: str, view_func: ft.RouteCallable, **options: Any) -> None:
        self.add_url_rule(rule, endpoint, view_func, methods=['QUERY'], **options)

    def method_view(self, name: str) -> Callable[[Type[MethodView]], Type[MethodView]]:
        def decorator(cls: Type[MethodView]) -> Type[MethodView]:
            cls.methods.append('QUERY')
            return super().method_view(name)(cls)
        return decorator

    def query(self, rule: str, **options: Any) -> Callable[[ft.RouteCallable], ft.RouteCallable]:
        def decorator(f: ft.RouteCallable) -> ft.RouteCallable:
            endpoint = options.pop('endpoint', None)
            if endpoint is None:
                endpoint = _endpoint_from_view_func(f)
            self.add_query_route(rule, endpoint, f, **options)
            return f
        return decorator

    def register_error_handler(self, code_or_exception: Union[int, type[Exception]], f: ft.ErrorHandlerCallable) -> None:
        exc_class, code = self._get_exc_class_and_code(code_or_exception)
        super().register_error_handler(code or exc_class, f)

    @staticmethod
def _get_exc_class_and_code(exc_class_or_code: Union[int, type[Exception]]) -> Tuple[type[Exception], Optional[int]]:
        if isinstance(exc_class_or_code, int):
            try:
                exc_class = default_exceptions[exc_class_or_code]
            except KeyError:
                raise ValueError(f"'{exc_class_or_code}' is not a recognized HTTP error code. Use a subclass of HTTPException with that code instead.") from None
        else:
            exc_class = exc_class_or_code

        if isinstance(exc_class, Exception):
            raise TypeError(f"{exc_class!r} is an instance, not a class. Handlers can only be registered for Exception classes or HTTP error codes.")

        if not issubclass(exc_class, Exception):
            raise ValueError(f"'{exc_class.__name__}' is not a subclass of Exception. Handlers can only be registered for Exception classes or HTTP error codes.")

        if issubclass(exc_class, HTTPException):
            return exc_class, exc_class.code
        else:
            return exc_class, None

views.http_method_funcs.add('QUERY')

__all__ = ['Scaffold']