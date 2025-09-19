from __future__ import annotations

from .. import builder as b

def unique(*args: b.RelationshipFieldRef|b.Relationship|b.RelationshipRef|b.RelationshipReading, model:b.Model|None=None) -> b.Expression|tuple[b.Expression, ...]:
    if not args:
        raise ValueError("unique expects at least 1 argument")
    if len(args) > 1:
        if not all(isinstance(a, b.RelationshipFieldRef) for a in args):
            raise TypeError("Not all items are relationship fields")
        uc = b.Unique(*args, model=model) # type: ignore
    else:
        assert args
        if isinstance(args[0], b.RelationshipFieldRef):
            uc = b.Unique(*args) # type: ignore
        elif isinstance(args[0], (b.Relationship, b.RelationshipRef, b.RelationshipReading)):
            rel = args[0]._relationship if isinstance(args[0], b.RelationshipRef) else args[0]
            if rel._arity() != 2:
                raise ValueError("Only binary relationships are allowed")
            uc = b.Unique(rel[1], model=model)
        else:
            raise TypeError("Unexpected argument type. Only relationship fields or relationships are allowed")
    return uc.to_expressions()
