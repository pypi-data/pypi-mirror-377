import datetime
from typing import TYPE_CHECKING, Literal

from bs4 import BeautifulSoup
from pbi_parsers import dax, pq
from pbi_parsers.pq.misc.external_sources import BaseExternalSource, get_external_sources
from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.logging import get_logger
from pbi_core.ssas.model_tables._group import RowNotFoundError
from pbi_core.ssas.model_tables.base import RefreshType, SsasRefreshRecord, SsasTable
from pbi_core.ssas.model_tables.enums import DataState
from pbi_core.ssas.server._commands import RefreshCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import DataView, PartitionMode, PartitionType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.expression import Expression
    from pbi_core.ssas.model_tables.query_group import QueryGroup
    from pbi_core.ssas.model_tables.table import Table


logger = get_logger()


class Partition(SsasRefreshRecord):
    """Partitions are a child of Tables. They contain the Power Query code.

    These are the physical segments of the table that contain the data.
    They cannot be edited within the Power BI Desktop UI, but can be edited in the
    Tabular Editor or other tools (like this one!). Data refreshes occur on the Partition-level.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/81badb81-31a8-482b-ae16-5fc9d8291d9e)
    """

    _default_refresh_type = RefreshType.FULL

    data_view: DataView
    data_source_id: int | None = None
    description: str | None = None
    error_message: str | None = None
    expression_source_id: int | None = None
    m_attributes: str | None = None
    mode: PartitionMode
    name: str
    partition_storage_id: int
    query_definition: str
    query_group_id: int | None = None
    range_granularity: int
    retain_data_till_force_calculate: bool
    state: DataState
    system_flags: int
    table_id: int
    type: PartitionType

    modified_time: datetime.datetime
    refreshed_time: datetime.datetime

    _commands: RefreshCommands = PrivateAttr(default_factory=lambda: SsasCommands.partition)

    def modification_hash(self) -> int:
        return hash(
            (
                self.data_view,
                self.data_source_id,
                self.description,
                # self.error_message,
                self.expression_source_id,
                self.m_attributes,
                self.mode,
                self.name,
                self.partition_storage_id,
                self.query_definition,
                self.query_group_id,
                self.range_granularity,
                self.retain_data_till_force_calculate,
                # self.state,
                # self.system_flags,
                self.table_id,
                self.type,
            ),
        )

    def expression_ast(self) -> dax.Expression | pq.Expression | None:
        if self.type == PartitionType.CALCULATED:
            ret = pq.to_ast(self.query_definition)
            if ret is None:
                msg = "Failed to parse DAX expression from partition query definition"
                raise ValueError(msg)
        elif self.type == PartitionType.M:
            ret = dax.to_ast(self.query_definition)
            if ret is None:
                msg = "Failed to parse M expression from partition query definition"
                raise ValueError(msg)
        else:
            logger.warning("Attempted to get AST of non-M/DAX partition", partition=self.name, type=self.type)
            return None

    def expression_source(self) -> "Expression | None":
        if self.expression_source_id is None:
            return None
        return self.tabular_model.expressions.find(self.expression_source_id)

    def is_system_table(self) -> bool:
        return bool(self.system_flags >> 1 % 2)

    def is_from_calculated_table(self) -> bool:
        return bool(self.system_flags % 2)

    def query_group(self) -> "QueryGroup | None":
        try:
            return self.tabular_model.query_groups.find({"id": self.table_id})
        except RowNotFoundError:
            return None

    def table(self) -> "Table":
        return self.tabular_model.tables.find({"id": self.table_id})

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        parent_nodes: list[SsasTable | None] = [self.table(), self.query_group()]
        parent_lineage: list[LineageNode] = [c.get_lineage(lineage_type) for c in parent_nodes if c is not None]
        return LineageNode(self, lineage_type, parent_lineage)

    def remove_columns(self, dropped_columns: "Iterable[Column | str | None]") -> BeautifulSoup:
        def pq_escape(x: str) -> str:
            """Beginning of column escaping for power query."""
            return x.replace('"', '""')

        """Adds a Table.RemoveColumns statement to the end of the Partition's PowerQuery.

        This means the upon refresh, the columns will not be included in the table
        """
        from pbi_core.ssas.model_tables.column import Column  # noqa: PLC0415

        new_dropped_columns: list[str] = []
        for col in dropped_columns:
            if isinstance(col, Column):
                # Tables have a column named "RowNumber-<UUID>" that cannot be removed in the PowerQuery
                if col._column_type() != "CALC_COLUMN" and not col.is_key:
                    assert col.explicit_name is not None, "Column must have an explicit name to be dropped"
                    new_dropped_columns.append(col.explicit_name)
            elif isinstance(col, str):
                new_dropped_columns.append(col)

        # TODO: create a powerquery parser to do this robustly
        new_dropped_columns = [pq_escape(x) for x in new_dropped_columns]
        logger.info("Updating partition to drop columns", table=self.table().name, columns=new_dropped_columns)
        lines = self.query_definition.split("\n")
        final_table_name = lines[-1].strip()
        setup = "\n".join(lines[:-2])

        prior_updates = setup.count("pbi_update")  # used to keep statement variables unique when applied multiple times
        new_final_table_name = f"pbi_update{prior_updates}"

        cols = ", ".join(f'"{x}"' for x in new_dropped_columns)
        setup += f",\n    {new_final_table_name} = Table.RemoveColumns({final_table_name}, {{{cols}}})"
        setup += f"\nin\n    {new_final_table_name}"
        self.query_definition = setup
        return self.alter()

    def external_sources(self) -> list[BaseExternalSource]:
        if self.type != PartitionType.M:
            return []
        return get_external_sources(self.query_definition)
