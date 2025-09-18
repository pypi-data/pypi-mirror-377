import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasRenameRecord, SsasTable
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.model import Model
    from pbi_core.ssas.model_tables.query_group import QueryGroup
from pbi_core.lineage import LineageNode


class Kind(IntEnum):
    M = 0


class Expression(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/61f98e45-d5e3-4435-b829-2f2f043839c1)
    """

    description: str | None = None
    expression: str
    kind: Kind
    model_id: int
    name: str
    parameter_values_column_id: int | None = None
    query_group_id: int | None = None

    lineage_tag: UUID = uuid4()
    source_lineage_tag: UUID = uuid4()

    modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.expression)

    def modification_hash(self) -> int:
        return hash((
            self.description,
            self.expression,
            self.kind,
            self.model_id,
            self.name,
            self.parameter_values_column_id,
            self.query_group_id,
            self.lineage_tag,
            self.source_lineage_tag,
        ))

    def model(self) -> "Model":
        return self.tabular_model.model

    def parameter_values_column(self) -> "Column | None":
        if self.parameter_values_column_id is None:
            return None
        return self.tabular_model.columns.find(self.parameter_values_column_id)

    def query_group(self) -> "QueryGroup | None":
        return self.tabular_model.query_groups.find({"id": self.query_group_id})

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        parent_nodes: list[SsasTable | None] = [self.model(), self.query_group()]
        parent_lineage = [p.get_lineage(lineage_type) for p in parent_nodes if p is not None]
        return LineageNode(self, lineage_type, parent_lineage)
