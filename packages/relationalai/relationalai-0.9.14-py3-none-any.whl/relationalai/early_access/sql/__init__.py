import warnings
from relationalai.semantics.sql import sql
from relationalai.semantics.sql.compiler import Compiler

__all__ = ["sql", "Compiler"]

warnings.warn(
    "relationalai.early_access.sql.* is deprecated. "
    "Please migrate to relationalai.semantics.sql.*",
    DeprecationWarning,
    stacklevel=2,
)