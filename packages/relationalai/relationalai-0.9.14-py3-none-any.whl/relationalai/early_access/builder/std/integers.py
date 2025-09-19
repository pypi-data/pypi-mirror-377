from __future__ import annotations
from typing import Any

from .. import builder as b

# Coerce a number to Int64.
def int64(value: b.Producer|int) -> b.ConceptMember:
    return b.ConceptMember(b.Int64, value, {})

# Coerce a number to Int128.
def int128(value: b.Producer|int) -> b.ConceptMember:
    return b.ConceptMember(b.Int128, value, {})

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

def parse_int64(value: b.Producer|str) -> b.Expression:
    return _make_expr("parse_int64", value, b.Int64.ref("res"))

def parse_int128(value: b.Producer|str) -> b.Expression:
    return _make_expr("parse_int128", value, b.Int128.ref("res"))

# Alias parse_int128 to parse
def parse(value: b.Producer|str) -> b.Expression:
    return parse_int128(value)