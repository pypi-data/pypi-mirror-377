import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.enums import DataState
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import MetadataPermission

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.role import Role
    from pbi_core.ssas.model_tables.table import Table


class TablePermission(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ac2ceeb3-a54e-4bf5-85b0-a770d4b1716e)
    """

    error_message: str | None = None
    filter_expression: str | None = None
    metadata_permission: MetadataPermission
    role_id: int
    state: DataState
    table_id: int

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.table_permission)

    def __repr__(self) -> str:
        return f"TablePermission(id={self.id}, role={self.role().name}, table={self.table()})"

    def modification_hash(self) -> int:
        return hash((
            # self.error_message,
            self.filter_expression,
            self.metadata_permission,
            self.role_id,
            # self.state,
            self.table_id,
        ))

    def role(self) -> "Role":
        return self.tabular_model.roles.find(self.role_id)

    def table(self) -> "Table":
        return self.tabular_model.tables.find(self.table_id)
