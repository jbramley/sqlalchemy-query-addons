from collections import defaultdict, deque
from typing import Optional, Self

from sqlalchemy import Select, TableClause, Table
from sqlalchemy.orm import InstrumentedAttribute, class_mapper
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql._typing import _JoinTargetArgument, _OnClauseArgument
from sqlalchemy.sql.elements import AnnotatedColumnElement
from sqlalchemy.sql.visitors import iterate


class SmartJoinsSelect(Select):
    join_graph: dict[TableClause, list[TableClause]] = defaultdict(list)

    def join(
        self,
        target: _JoinTargetArgument,
        onclause: Optional[_OnClauseArgument] = None,
        *,
        isouter: bool = False,
        full: bool = False,
    ) -> Self:
        """
        Intercept the base join() to generate a join graph used by `fix_joins()` to determine whether a join is part of
        a transitive relationship that needs an inner join
        """
        # TODO: allow user to force inner or outer join
        # TODO: handle aliasing
        match target:
            case InstrumentedAttribute():
                self.join_graph[target.property.target].append(target.parent.tables[0])
            case DeclarativeAttributeIntercept():
                target_table = class_mapper(target).tables[0]
                if onclause is not None:
                    for e in iterate(onclause):
                        if (
                            isinstance(e, AnnotatedColumnElement)
                            and e.table != target_table
                        ):
                            self.join_graph[target_table].append(e.table)
            case AliasedClass():
                print(target)
        return super().join(target, onclause, isouter=isouter, full=full)

    def fix_joins(self):
        """
        Updates the join type (inner vs. outer) based on whether the joined table is used in the filter (inner) or not
        (outer). This is a relatively naive approach that is likely out-classed by Django's JoinPromoter.
        """
        filter_tables = set()
        for e in iterate(self.whereclause):
            if isinstance(e, AnnotatedColumnElement):
                filter_tables.add(e.table)
                q = deque(self.join_graph.get(e.table, []))
                while q:
                    t = q.popleft()
                    filter_tables.add(t)
                    q.extend(self.join_graph.get(t, []))
        for j in self._setup_joins:
            if isinstance(j[0], InstrumentedAttribute):
                table = j[0].property.target
            elif isinstance(j[0], Table):
                table = j[0]
            else:
                print(f"Unexpected join target: {j[0]!r}")
            j[3]["isouter"] = table not in filter_tables
