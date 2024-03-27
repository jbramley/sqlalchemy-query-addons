from typing import cast

from sqlalchemy import sql
from sqlalchemy.orm.context import ORMSelectCompileState

from sqlalchemy_query_addons.smartjoins._select import SmartJoinsSelect


@sql.base.CompileState.plugin_for("orm", "select")
class SmartJoinsORMSelectCompileState(ORMSelectCompileState):
    def _setup_for_generate(self):
        query = cast(SmartJoinsSelect, self.select_statement)
        query.fix_joins()
        super()._setup_for_generate()
