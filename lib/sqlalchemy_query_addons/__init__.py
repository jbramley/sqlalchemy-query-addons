from typing import Any

from sqlalchemy import Select
from sqlalchemy.sql._typing import _ColumnsClauseArgument

from sqlalchemy_query_addons.smartjoins._select import SmartJoinsSelect
from sqlalchemy_query_addons.smartjoins._compile_state import (
    SmartJoinsORMSelectCompileState as SmartJoinsORMSelectCompileState,
)


def select(*entities: _ColumnsClauseArgument[Any], **__kw: Any) -> Select[Any]:
    return SmartJoinsSelect(*entities)
