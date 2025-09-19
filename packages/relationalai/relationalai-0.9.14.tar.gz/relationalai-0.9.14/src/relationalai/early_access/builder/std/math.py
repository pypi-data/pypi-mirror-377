from __future__ import annotations

from .. import builder as b
from .std import _Number, _make_expr

def abs(value: _Number) -> b.Expression:
    return _make_expr("abs", value, b.Number.ref("res"))

def natural_log(value: _Number) -> b.Expression:
    return _make_expr("natural_log", value, b.Number.ref("res"))

def sqrt(value: _Number) -> b.Expression:
    return _make_expr("sqrt", value, b.Number.ref("res"))

def maximum(left: _Number, right: _Number) -> b.Expression:
    return _make_expr("maximum", left, right, b.Number.ref("res"))

def minimum(left: _Number, right: _Number) -> b.Expression:
    return _make_expr("minimum", left, right, b.Number.ref("res"))

def isinf(value: _Number) -> b.Expression:
    return _make_expr("isinf", value)

def isnan(value: _Number) -> b.Expression:
    return _make_expr("isnan", value)

def ceil(value: _Number) -> b.Expression:
    return _make_expr("ceil", value, b.Number.ref("res"))

def floor(value: _Number) -> b.Expression:
    return _make_expr("floor", value, b.Number.ref("res"))