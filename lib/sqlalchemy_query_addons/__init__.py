from typing import Any

from sqlalchemy import Select
from sqlalchemy.sql._typing import _ColumnsClauseArgument

from sqlalchemy_query_addons.smartjoins import (
    SmartJoinsSelect,
    SmartJoinsORMSelectCompileState as SmartJoinsORMSelectCompileState,
)


def select(*entities: _ColumnsClauseArgument[Any], **__kw: Any) -> Select[Any]:
    return SmartJoinsSelect(*entities)
