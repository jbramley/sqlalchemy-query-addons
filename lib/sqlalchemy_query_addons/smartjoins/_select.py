from collections import defaultdict, deque
from typing import Optional, Self, cast, NewType

from sqlalchemy import Select, Table, inspect, Subquery
from sqlalchemy.orm import InstrumentedAttribute, class_mapper, QueryableAttribute
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept
from sqlalchemy.orm.util import AliasedClass, AliasedInsp
from sqlalchemy.sql._typing import _JoinTargetArgument, _OnClauseArgument
from sqlalchemy.sql.annotation import AnnotatedAlias
from sqlalchemy.sql.elements import AnnotatedColumnElement
from sqlalchemy.sql.visitors import iterate


_JoinName = NewType("_JoinName", str)


class SmartJoinsSelect(Select):
    join_graph: dict[_JoinName, list[_JoinName]] = defaultdict(list)

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
        match target:
            case QueryableAttribute(property=prop, parent=parent):
                self.join_graph[_JoinName(prop.target.name)].append(
                    _JoinName(parent.selectable.name)
                )
            case DeclarativeAttributeIntercept():
                target_table = class_mapper(target).selectable.name
                if onclause is not None:
                    for e in iterate(onclause):
                        if (
                            isinstance(e, AnnotatedColumnElement)
                            and e.table.name != target_table
                        ):
                            self.join_graph[_JoinName(target_table)].append(
                                _JoinName(e.table.name)
                            )
            case AliasedClass():
                insp = cast(AliasedInsp, inspect(target))
                target_table = insp.name
                if onclause is not None:
                    for e in iterate(onclause):
                        if (
                            isinstance(e, AnnotatedColumnElement)
                            and e.table.name != target_table
                        ):
                            self.join_graph[_JoinName(target_table)].append(
                                _JoinName(e.table.name)
                            )
            case Subquery(name=name):
                if onclause is not None:
                    for e in iterate(onclause):
                        if (
                            isinstance(e, AnnotatedColumnElement)
                            and e.table.name != name
                        ):
                            self.join_graph[_JoinName(name)].append(
                                _JoinName(e.table.name)
                            )
        return super().join(target, onclause, isouter=isouter, full=full)

    def fix_joins(self):
        """
        Updates the join type (inner vs. outer) based on whether the joined table is used in the filter (inner) or not
        (outer). This is a relatively naive approach that is likely out-classed by Django's JoinPromoter.
        """
        filter_tables = set()
        for e in iterate(self.whereclause):
            if isinstance(e, AnnotatedColumnElement):
                filter_tables.add(e.table.name)
                q = deque(self.join_graph.get(_JoinName(e.table.name), []))
                while q:
                    t = q.popleft()
                    filter_tables.add(t)
                    q.extend(self.join_graph.get(t, []))
        for j in self._setup_joins:
            # noinspection PyUnresolvedReferences
            match j[0]:
                case InstrumentedAttribute(property=prop):
                    table = prop.target.name
                case Table(name=name):
                    table = name
                case Subquery(name=name):
                    table = name
                case AnnotatedAlias(name=name):
                    table = name
                case _:
                    raise ValueError(f"Unknown join type: {j[0]}")
            j[3]["isouter"] = table not in filter_tables
