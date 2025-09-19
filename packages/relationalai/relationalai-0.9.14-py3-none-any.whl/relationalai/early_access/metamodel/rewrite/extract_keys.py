from __future__ import annotations

from relationalai.early_access.metamodel import ir
from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel.visitor import Visitor, Rewriter
from relationalai.early_access.metamodel.util import OrderedSet
from relationalai.early_access.metamodel import helpers, factory as f, types, builtins
from typing import Optional, Any, Iterable
from collections import defaultdict

# Given an Output with a group of keys (some of them potentially null),
# * extract the lookups that bind (transitively) all the keys
# * extract the lookups that bind (transitively) properties of the keys
# * generate all the valid combinations of keys being present or not
#   * first all keys are present,
#   * then we remove one key at a time,
#   * then we remove two keys at a time,and so on.
#   * the last combination is when all the *nullable* keys are missing.
# * for each combination:
#   * create a compound (hash) key
#   * create a Logical that:
#       * contains all the relevant lookups for keys and properties
#       * contains negated lookups for null keys
#       * outputs using the compound key
#
# E.g., we go from
#
# Logical
#     Foo(foo)
#     rel1(foo, x)
#     Logical ^[v1=None]
#         rel2(foo, v1)
#     Logical ^[v2=None, k2=None]
#         rel3(foo, k2)
#         rel4(k2, v2)
#     Logical ^[v3=None, k3=None]
#         rel5(foo, y)
#         rel6(y, k3)
#         rel7(k3, v3)
#     output[foo, k2, k3](v1, v2, v3)
#
# to
#
# Logical
#     Logical
#         Logical
#             Foo(foo)
#             rel1(foo, x)
#             Logical ^[k2=None, k3=None]
#                 rel3(foo, k2)
#                 rel5(foo, y)
#                 rel6(y, k3)
#             Logical ^[v1=None]
#                 rel2(foo, v1)
#             Logical ^[v2=None, k2=None]
#                 rel4(k2, v2)
#             Logical ^[v3=None, k3=None]
#                 rel7(k3, v3)
#             construct(Hash, "Foo", foo, "Concept2", k2, "Concept3", k3, compound_key)
#             output[compound_key](v1, v2, v3)
#         Logical
#             Foo(foo)
#             rel1(foo, x)
#             Logical ^[k2=None, k3=None]
#                 rel5(foo, y)
#                 rel6(y, k3)
#             Not
#                 Logical
#                     rel3(foo, k2)
#             Logical ^[v1=None]
#                 rel2(foo, v1)
#             Logical ^[v3=None, k3=None]
#                 rel7(k3, v3)
#             construct(Hash, "Foo", foo, "Concept3", k3, compound_key)
#             output[compound_key](v1, None, v3)
#         Logical
#             Foo(foo)
#             rel1(foo, x)
#             Logical ^[k2=None, k3=None]
#                 rel3(foo, k2)
#                 rel5(foo, y)
#             Not
#                 Logical
#                     rel6(y, k3)
#             Logical ^[v1=None]
#                 rel2(foo, v1)
#             Logical ^[v2=None, k2=None]
#                 rel4(k2, v2)
#             construct(Hash, "Foo", foo, "Concept2", k2, compound_key)
#             output[compound_key](v1, v2, None)
#         Logical
#             Foo(foo)
#             rel1(foo, x)
#             Logical ^[k2=None, k3=None]
#                 rel5(foo, y)
#             Not
#                 Logical
#                     rel3(foo, k2)
#                     rel6(y, k3)
#             Logical ^[v1=None]
#                 rel2(foo, v1)
#             construct(Hash, "Foo", foo, compound_key)
#             output[compound_key](v1, None, None)

class ExtractKeys(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        visitor = IdentifyKeysVisitor()
        model.accept(visitor)
        return ExtractKeysRewriter(visitor).walk(model)

class ExtractInfo:
    def __init__(self, vars_to_extract: OrderedSet[ir.Var]):
        self.original_keys = vars_to_extract
        # the subsets of the original keys that are nullable or not.
        self.non_nullable_keys: OrderedSet[ir.Var] = OrderedSet()
        self.nullable_keys: OrderedSet[ir.Var] = OrderedSet()

        # lookup tasks that transitively bind all the key vars
        # e.g., if the key is Z, in foo(X, Y), bar(Y, Z), baz(Z, W)
        # we extract foo(X, Y), bar(Y, Z)
        self.key_lookups: list[ir.Task] = []

        # lookup tasks that transitively bind all the properties of the keys
        # e.g., if the key is Z, in bar(Y, Z), baz(Z, W), qux(W, V)
        # we extract baz(Z, W), qux(W, V).
        # store the lookups by key. each key might bind multiple properties, each list in
        # dict keeps track of one of these properties
        self.inner_property_lookups: dict[ir.Var, list[OrderedSet[ir.Task]]] = defaultdict(list)

        # other top-level tasks that are not key lookups. These need to be kept in each
        # match case of the rewritten Logical.
        self.non_key_top_level_tasks: list[ir.Task] = []

        # the original output task. New outputs are generated based on the keys and
        # properties in the original output
        self.original_output: Optional[ir.Output] = None

        # variables coming from concept lookups, that are not nullable
        # this includes lookups at the top-level, as well as inside logicals when
        # hoisted without a None default.
        self.non_nullable_vars: OrderedSet[ir.Var] = OrderedSet()

class IdentifyKeysVisitor(Visitor):
    def __init__(self):
        self.extract_info_for_logical: dict[ir.Logical, ExtractInfo] = {}
        self.curr_info = None

    def enter(self, node: ir.Node, parent: Optional[ir.Node]=None) -> Visitor:
        if isinstance(node, ir.Logical):
            outputs = [x for x in node.body if isinstance(x, ir.Output) and x.keys]
            if not outputs:
                return self
            assert len(outputs) == 1, "multiple outputs with keys in a logical"
            if not outputs[0].keys:
                return self

            # Logical with an output that has keys
            info = ExtractInfo(OrderedSet.from_iterable(outputs[0].keys))

            # Set the original output
            info.original_output = outputs[0]

            # The original keys and any intermediate vars needed to correctly bind the keys.
            # Any transitive key vars are added during the `find_key_lookups_fixpoint` calls
            extended_keys:OrderedSet[ir.Var] = OrderedSet.from_iterable(outputs[0].keys)

            # First, collect all the top-level lookups
            top_level_lookups = []
            for task in node.body:
                if isinstance(task, ir.Lookup):
                    top_level_lookups.append(task)

            # Find all the key lookups at the top level. Property lookups are handled later
            # and stored in non_key_top_level_tasks
            key_lookups = self.find_key_lookups_fixpoint(top_level_lookups, extended_keys)

            # Then, deal with lookups inside logicals (with hoisted defaults)
            for task in node.body:
                processed = False

                # Top-level concept lookups identify variables that are not nullable
                if isinstance(task, ir.Lookup) and helpers.is_concept_lookup(task):
                    vars = helpers.vars(task.args)
                    if vars[0] not in info.non_nullable_vars:
                        info.non_nullable_vars.add(vars[0])

                if isinstance(task, ir.Logical):
                    for h in task.hoisted:
                        # Hoisted vars without a default are not nullable
                        if isinstance(h, ir.Var):
                            info.non_nullable_vars.add(h)
                        elif isinstance(h, ir.Default):
                            # Hoisted vars with a non-None default are not nullable
                            if h.value is not None:
                                info.non_nullable_vars.add(h.var)
                            elif h.var in info.original_keys and h.var not in info.non_nullable_vars:
                                info.nullable_keys.add(h.var)

                    # Find key lookups inside the logical
                    current_lookups = self.find_key_lookups_fixpoint(task.body, extended_keys)
                    key_lookups.update(current_lookups)

                    # Find property lookups inside the logical. Assume that each logical
                    # binds a separate property for each key
                    current_property_lookups = self.find_property_lookups_fixpoint(task.body, extended_keys)
                    for k, v in current_property_lookups.items():
                        info.inner_property_lookups[k].append(v)

                    if current_lookups or current_property_lookups:
                        processed = True

                if task in key_lookups:
                    continue

                # If the task does not contain key or property lookups, then we need to
                # maintain these at the top level during the actual rewrite
                if not processed and \
                    (
                        isinstance(task, ir.Logical) or \
                        isinstance(task, ir.Lookup) or \
                        isinstance(task, ir.Construct) or \
                        isinstance(task, ir.Aggregate) or \
                        isinstance(task, ir.Rank)
                    ):
                    info.non_key_top_level_tasks.append(task)

            info.non_nullable_keys = info.original_keys - info.nullable_keys
            info.key_lookups = list(key_lookups)

            # we only need to transform the logical if there are nullable keys
            if info.nullable_keys:
                self.extract_info_for_logical[node] = info
                self.curr_info = info
        return self

    def leave(self, node: ir.Node, parent: Optional[ir.Node]=None) -> ir.Node:
        if not self.curr_info:
            return node

        if isinstance(node, ir.Aggregate):
            # we assume that variables appearing in aggregate group-by's are not nullable
            for v in node.group:
                if v in self.curr_info.nullable_keys:
                    self.curr_info.nullable_keys.remove(v)
        elif isinstance(node, ir.Logical) and node in self.extract_info_for_logical:
            # if the set of nullable keys became empty, we shouldn't attempt to transform the logical
            if not self.curr_info.nullable_keys:
                self.extract_info_for_logical.pop(node)
            self.curr_info = None

        return node

    def find_key_lookups_fixpoint(self, tasks:Iterable[ir.Task], keys:OrderedSet[ir.Var]):
        # lookups with a single argument correspond to concepts.
        # we should keep them ahead of the other lookups.
        concept_lookups = OrderedSet()
        # for lookups with multiple arguments, we start from those that have a key as the last
        # argument and move backwards. that's why each time we insert at the front of the list
        lookups = OrderedSet()

        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in tasks:
                if isinstance(task, ir.Lookup) and task not in lookups and task not in concept_lookups:
                    vars = helpers.vars(task.args)
                    if len(vars) == 1 and vars[0] in keys:
                        concept_lookups.add(task)
                        there_is_progress = True
                    elif len(vars) > 1 and all(v in keys for v in vars[1:]):
                        assert isinstance(vars[0], ir.Var)
                        keys.add(vars[0])
                        lookups.prepend(task)
                        there_is_progress = True

        return concept_lookups | lookups

    def find_property_lookups_fixpoint(self, tasks:Iterable[ir.Task], keys:Iterable[ir.Var]):
        property_lookups = defaultdict(OrderedSet)

        # Keep track of transitive vars seen for each key
        seen_vars: dict[ir.Var, set[ir.Var]] = {k: set([k]) for k in keys}

        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in tasks:
                if isinstance(task, ir.Lookup):
                    vars = task.args
                    if len(vars) <= 1:
                        # Singleton lookups cannot be for properties
                        continue
                    if any(task in v for v in property_lookups.values()):
                        # Already seen this lookup - don't add it again
                        continue
                    for (var, inter_vars) in seen_vars.items():
                        if any(nv in vars for nv in inter_vars):
                            # If there are any other keys in the lookup, then it is not
                            # purely a lookup of this key's properties
                            #
                            # TODO: handle the case where there are multiple keys for a
                            # single property.
                            if any(isinstance(v, ir.Var) and v in keys and v != var for v in vars):
                                continue

                            # If any seen var is in the args
                            property_lookups[var].add(task)
                            seen_vars[var].update([v for v in vars if isinstance(v, ir.Var)])
                            there_is_progress = True
                elif isinstance(task, ir.Construct):
                    if any(task in v for v in property_lookups.values()):
                        continue
                    for (var, inter_vars) in seen_vars.items():
                        if task.id_var in inter_vars:
                            property_lookups[var].add(task)
                            there_is_progress = True

        return property_lookups

class ExtractKeysRewriter(Rewriter):
    def __init__(self, visitor: IdentifyKeysVisitor):
        super().__init__()
        self.visitor = visitor

    def handle_logical(self, node: ir.Logical, parent: ir.Node, ctx:Optional[Any]=None) -> ir.Logical:
        new_body = self.walk_list(node.body, node)

        # We are in a logical with an output at this level.
        if node in self.visitor.extract_info_for_logical:
            info = self.visitor.extract_info_for_logical[node]

            # Update the key sets based on the identified non-nullable vars
            # remove nullable keys that were inferred to be non-nullable,
            # and add them to the non-nullable set
            non_null_nullable_keys = info.nullable_keys & info.non_nullable_vars
            info.non_nullable_keys.update(non_null_nullable_keys)
            info.nullable_keys = info.nullable_keys - info.non_nullable_vars

            # Get the key lookups. Each output case will start with these lookups
            top_level_key_lookups = list(info.key_lookups)

            # Create a compound key that will be used in place of the original keys.
            compound_key = f.var("compound_key", types.Hash)

            # Get all cases for each combination of null/non-null keys
            match_cases = self._nullable_key_combinations(info, top_level_key_lookups, compound_key)

            return f.logical(tuple(match_cases), [])
        else:
            return node if new_body is node.body else f.logical(new_body, node.hoisted)

    # Generate all the combinations of nullable keys being present or not.
    # For each such combination, generate a list of lookups that will be used in the Match.
    # In total, return a list of lists of lookups, covering all the Match cases.
    def _nullable_key_combinations(
            self,
            info:ExtractInfo,
            inner_key_lookups:list[ir.Task],
            compound_key:ir.Var):
        return self._nullable_key_combinations_rec(info, [], 0, inner_key_lookups, compound_key)

    def _nullable_key_combinations_rec(
            self,
            info: ExtractInfo,
            nullable_non_null_keys: list[ir.Var],
            idx: int,
            inner_key_lookups: list[ir.Task],
            compound_key:ir.Var):

        if idx < len(info.nullable_keys):
            key = info.nullable_keys[idx]
            case1_list = self._nullable_key_combinations_rec(info, nullable_non_null_keys + [key], idx + 1, inner_key_lookups, compound_key)
            case2_list = self._nullable_key_combinations_rec(info, nullable_non_null_keys, idx + 1, inner_key_lookups, compound_key)
            case1_list.extend(case2_list)
            return case1_list
        else:
            # Create a copy to mutate
            inner_key_lookups_ = list(inner_key_lookups)

            # Make sure the orig output is set
            assert isinstance(info.original_output, ir.Output)

            curr_non_null_keys = OrderedSet[ir.Var]()
            curr_null_keys = OrderedSet[ir.Var]()
            for key in info.original_keys:
                if key in info.non_nullable_keys or key in nullable_non_null_keys:
                    curr_non_null_keys.add(key)
                else:
                    curr_null_keys.add(key)

            removed_lookups = self._remove_from_key_lookups(inner_key_lookups_, curr_null_keys, curr_non_null_keys)

            # Build the inner lookups.
            # Start with the non-null key lookups. Wrap these in a logical where the non-null
            # keys are hoisted
            inner_lookups: list[ir.Task] = [f.logical(inner_key_lookups_, list(curr_non_null_keys))]

            # Add other top-level tasks that are not key or property lookups
            inner_lookups.extend(info.non_key_top_level_tasks)

            # Add negated lookups for each null key
            if removed_lookups:
                for (_, removed) in removed_lookups.items():
                    if len(removed) == 1:
                        negated_null_key_lookups = f.not_(removed[0])
                    else:
                        negated_null_key_lookups = f.not_(f.logical(removed, []))
                    inner_lookups.append(negated_null_key_lookups)

            # Add property lookups for each non-null key
            for key in curr_non_null_keys:
                for tasks in info.inner_property_lookups.get(key, []):
                    # Create a separate logical for each key's property lookups. This is
                    # needed so that flatten can split the dependencies correctly
                    prop_lookups = []
                    hoisted_prop_vars = OrderedSet()
                    for task in tasks:
                        if task not in prop_lookups:
                            prop_lookups.append(task)
                            assert isinstance(task, ir.Lookup)

                            # only care about hoisting properties that are in the output
                            vars = helpers.vars(task.args)
                            output_vars = helpers.output_vars(info.original_output.aliases)
                            hoisted_prop_vars.update([v for v in vars if v in output_vars])
                    if prop_lookups:
                        hoisted_props = [ir.Default(v, None) for v in hoisted_prop_vars]
                        inner_lookups.append(f.logical(prop_lookups, hoisted_props))

            # Create the arguments for constructing the compound key. Only include the
            # values for non-null keys. Null key names are still included.
            values: list[ir.Value] = [compound_key.type]
            for key in info.original_keys:
                assert isinstance(key.type, ir.ScalarType)
                values.append(ir.Literal(types.String, key.type.name))
                if key in curr_non_null_keys:
                    values.append(key)
            inner_lookups.append(ir.Construct(
                None,
                tuple(values),
                compound_key,
                OrderedSet().frozen()
            ))

            # Add the output for this combination of null/non-null keys.
            # First, get the annos
            annos = list(info.original_output.annotations)

            if info.original_output.keys:
                annos.append(f.annotation(builtins.output_keys, tuple(info.original_output.keys)))

            # Then, construct the output aliases. Drop the arguments that are either
            # properties of currently null keys or the null keys themselves
            curr_null_keys_or_properties = OrderedSet[ir.Var]()
            output_vars = helpers.output_vars(info.original_output.aliases)
            for key in curr_null_keys:
                for tasks in info.inner_property_lookups.get(key, []):
                    for task in tasks:
                        assert isinstance(task, ir.Lookup)
                        vars = helpers.vars(task.args)
                        curr_null_keys_or_properties.update([v for v in vars if v in output_vars])
                if key in output_vars:
                    curr_null_keys_or_properties.add(key)

            new_output_aliases = []
            for (alias, var) in info.original_output.aliases:
                # Need a placeholder (None) for this output var so that columns still
                # line up. This will be excluded later during Flatten so we don't
                # actually output None values.
                out_var = None if var in curr_null_keys_or_properties else var
                new_output_aliases.append((alias, out_var))
            inner_lookups.append(f.output(new_output_aliases, [compound_key], annos=annos))

            return [f.logical(inner_lookups, [])]

    # Null keys should not be looked up. Non-nullable keys should also not be looked up,
    # since they will be looked up separately in their own logical.
    #
    # Returns the removed lookups as a dict mapping from key to lookups
    def _remove_from_key_lookups(self, lookups: list[ir.Task], vars_to_purge: OrderedSet[ir.Var], non_nullable_keys: OrderedSet[ir.Var]):
        removed = defaultdict(list)
        # keep track of transitive keys too
        keys = [[v] for v in vars_to_purge]

        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in lookups:
                assert isinstance(task, ir.Lookup)
                vars = helpers.vars(task.args)
                for ks in keys:
                    if vars[-1] in ks:
                        lookups.remove(task)
                        # ks[0] is the original key that led to this chain of lookups
                        removed[ks[0]].append(task)
                        new_vars = [v for v in vars if v not in vars_to_purge and v not in non_nullable_keys]
                        ks.extend(new_vars)
                        there_is_progress = True
                        break

        return removed
