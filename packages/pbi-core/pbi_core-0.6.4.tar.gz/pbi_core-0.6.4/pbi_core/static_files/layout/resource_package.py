from enum import IntEnum

from ._base_node import LayoutNode


class ResourcePackageItemType(IntEnum):
    JS = 0
    CSS = 1
    PNG = 3
    PBIVIZ = 5
    NA = 100
    TOPO = 200
    JSON2 = 201
    JSON = 202


class ResourcePackageItem(LayoutNode):
    name: str | None = None
    path: str
    type: ResourcePackageItemType
    resourcePackageId: int | None = None
    resourcePackageItemBlobInfoId: int | None = None
    id: int | None = None


class ResourcePackageDetailsType(IntEnum):
    JS = 0
    CUSTOM_THEME = 1
    BASE_THEME = 2


class ResourcePackageDetails(LayoutNode):
    disabled: bool = False
    items: list[ResourcePackageItem] = []
    type: ResourcePackageDetailsType
    name: str
    id: int | None = None
    reportId: int | None = None


class ResourcePackage(LayoutNode):
    resourcePackage: ResourcePackageDetails
