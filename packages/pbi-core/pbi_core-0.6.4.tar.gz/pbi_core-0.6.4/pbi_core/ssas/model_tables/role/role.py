import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import ModelPermission

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.model import Model
    from pbi_core.ssas.model_tables.table_permission import TablePermission


class Role(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/94a8e609-b1ae-4814-b8dc-963005eebade)
    """

    description: str | None = None
    model_id: int
    model_permission: ModelPermission
    name: str

    modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.role)

    def modification_hash(self) -> int:
        return hash((
            self.description,
            self.model_id,
            self.model_permission,
            self.name,
        ))

    def model(self) -> "Model":
        return self.tabular_model.model

    def table_permissions(self) -> list["TablePermission"]:
        return [tp for tp in self.tabular_model.table_permissions if tp.role_id == self.id]
