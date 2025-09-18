from typing import Any

from pydantic import Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector


class PageInformationProperties(LayoutNode):
    pageInformationName: Any = None
    pageInformationQnaPodEnabled: Any = None
    pageInformationAltName: Any = None
    pageInformationType: Any = None


class PageInformation(LayoutNode):
    selector: Selector | None = None
    """Defines the scope at which to apply the formatting for this object.
    Can also define rules for matching highlighted values and how multiple definitions for the same property should
    be ordered."""
    properties: PageInformationProperties = Field(default_factory=PageInformationProperties)
    """Describes the properties of the object to apply formatting changes to."""


class PageSizeProperties(LayoutNode):
    pageSizeTypes: Any = None
    pageSizeWidth: Any = None
    pageSizeHeight: Any = None


class PageSize(LayoutNode):
    selector: Selector | None = None
    properties: PageSizeProperties = Field(default_factory=PageSizeProperties)


class BackgroundProperties(LayoutNode):
    color: Any = None
    image: Any = None
    transparency: Any = None


class Background(LayoutNode):
    selector: Selector | None = None
    properties: BackgroundProperties = Field(default_factory=BackgroundProperties)


class DisplayAreaProperties(LayoutNode):
    verticalAlignment: Any = None


class DisplayArea(LayoutNode):
    selector: Selector | None = None
    properties: DisplayAreaProperties = Field(default_factory=DisplayAreaProperties)


class OutspacePaneProperties(LayoutNode):
    backgroundColor: Any = None
    transparency: Any = None
    foregroundColor: Any = None
    titleSize: Any = None
    searchTextSize: Any = None
    headerSize: Any = None
    fontFamily: Any = None
    border: Any = None
    borderColor: Any = None
    checkboxAndApplyColor: Any = None
    inputBoxColor: Any = None
    width: Any = None


class OutspacePane(LayoutNode):
    selector: Selector | None = None
    properties: OutspacePaneProperties = Field(default_factory=OutspacePaneProperties)


class FilterCardProperties(LayoutNode):
    backgroundColor: Any = None
    transparency: Any = None
    border: Any = None
    borderColor: Any = None
    foregroundColor: Any = None
    textSize: Any = None
    fontFamily: Any = None
    inputBoxColor: Any = None


class FilterCard(LayoutNode):
    selector: Selector | None = None
    properties: FilterCardProperties = Field(default_factory=FilterCardProperties)


class PageRefreshProperties(LayoutNode):
    show: Any = None
    refreshType: Any = None
    duration: Any = None
    dialogLauncher: Any = None
    measure: Any = None
    checkEvery: Any = None


class PageRefresh(LayoutNode):
    selector: Selector | None = None
    properties: PageRefreshProperties = Field(default_factory=PageRefreshProperties)


class PersonalizeVisualProperties(LayoutNode):
    show: Any = None
    perspectiveRef: Any = None
    applyToAllPages: Any = None


class PersonalizeVisual(LayoutNode):
    selector: Selector | None = None
    properties: PersonalizeVisualProperties = Field(default_factory=PersonalizeVisualProperties)


class PageFormattingObjects(LayoutNode):
    pageInformation: list[PageInformation] = Field(default_factory=lambda: [PageInformation()])
    pageSize: list[PageSize] = Field(default_factory=lambda: [PageSize()])
    background: list[Background] = Field(default_factory=lambda: [Background()])
    displayArea: list[DisplayArea] = Field(default_factory=lambda: [DisplayArea()])
    outspace: list[Background] = Field(default_factory=lambda: [Background()])  # This is in fact a Background
    outspacePane: list[OutspacePane] = Field(default_factory=lambda: [OutspacePane()])
    filterCard: list[FilterCard] = Field(default_factory=lambda: [FilterCard()])
    pageRefresh: list[PageRefresh] = Field(default_factory=lambda: [PageRefresh()])
    personalizeVisuals: list[PersonalizeVisual] = Field(default_factory=lambda: [PersonalizeVisual()])
