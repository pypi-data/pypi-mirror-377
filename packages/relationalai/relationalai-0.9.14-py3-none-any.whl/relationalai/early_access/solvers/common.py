from __future__ import annotations

from typing import Any
from relationalai.early_access.builder import builder as b, std

def make_name(*args, sep: str | None = "_"):
    if not args:
        raise ValueError("No arguments provided to `make_name`")
    elif len(args) == 1:
        arg = args[0]
        if isinstance(arg, str):
            return arg
        elif isinstance(arg, list):
            return make_name(*arg, sep=sep)
        else:
            return std.strings.string(arg)
    elif sep:
        str_args = []
        for a in args:
            str_args.append(std.strings.string(a))
            str_args.append(sep)
        str_args.pop()
    else:
        str_args = map(std.strings.string, args)
    return std.strings.concat(*str_args)

# TODO move to std? need to support normal logical evaluation.
def all_different(*args: Any) -> b.Aggregate:
    return b.Aggregate(b.Relationship.builtins["all_different"], *args)

def implies(left, right) -> b.Expression:
    return b.Expression(b.Relationship.builtins["implies"], left, right)
