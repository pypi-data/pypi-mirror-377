import datetime
from typing import TYPE_CHECKING, Literal

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasReadonlyRecord
from pbi_core.ssas.model_tables.enums import DataState

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.level import Level


class AttributeHierarchy(SsasReadonlyRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/93d1844f-a6c7-4dda-879b-2e26ed5cd297)
    """

    attribute_hierarchy_storage_id: int
    column_id: int
    state: DataState

    modified_time: datetime.datetime
    refreshed_time: datetime.datetime

    def modification_hash(self) -> int:
        return hash((
            self.attribute_hierarchy_storage_id,
            self.column_id,
            self.state,
        ))

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return self.column().pbi_core_name()

    def column(self) -> "Column":
        return self.tabular_model.columns.find({"id": self.column_id})

    def levels(self) -> set["Level"]:
        return self.tabular_model.levels.find_all({"hierarchy_id": self.id})

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type, [level.get_lineage(lineage_type) for level in self.levels()])
        return LineageNode(self, lineage_type, [self.column().get_lineage(lineage_type)])
