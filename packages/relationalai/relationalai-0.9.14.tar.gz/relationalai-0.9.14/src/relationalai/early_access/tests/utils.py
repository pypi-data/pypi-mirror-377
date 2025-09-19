from itertools import count
from relationalai.early_access.metamodel import ir, types
from relationalai.early_access.builder import builder
from relationalai.early_access.builder.snowflake import Table

def reset_state():
    """
    Reset global state for consistent test snapshots.

    When we execute a pyrel program we accumulate some state, such as custom decimals, and
    we increase the counter for object ids. This function resets those counters and other
    state to a known baseline to ensure that test snapshots are consistent if we run the
    test alone vs in a suite of tests.
    """
    # reset the global id counters
    ir._global_id = count(10000)
    builder._global_id = count(10000)

    # Used to generate error source IDs
    builder.errors.ModelError.error_locations.clear()

    # reset the ErrorConcept state, so that Error.new() always generates the same IR
    builder.ErrorConcept._error_props.clear()
    builder.ErrorConcept._relation = None
    builder.ErrorConcept._overloads.clear()

    # caches of custom decimals
    for k in list(types._decimal_types.keys()):
        if types._decimal_types[k] != types.Decimal:
            del types._decimal_types[k]
    for k in list(builder.Concept.builtins):
        if k.startswith("Decimal(") and builder.Concept.builtins[k] is not builder.Decimal:
            del builder.Concept.builtins[k]

    # clear any cached Table sources
    Table._used_sources.clear()