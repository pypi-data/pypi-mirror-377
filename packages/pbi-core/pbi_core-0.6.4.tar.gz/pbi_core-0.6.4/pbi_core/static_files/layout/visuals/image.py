from pydantic import Field

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import BaseVisual
from .properties.base import Expression


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        imageUrl: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class ImageScalingProperties(LayoutNode):
    class _ImageScalingPropertiesHelper(LayoutNode):
        imageScalingType: Expression | None = None

    properties: _ImageScalingPropertiesHelper = Field(default_factory=_ImageScalingPropertiesHelper)


class ImageProperties(LayoutNode):
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    imageScaling: list[ImageScalingProperties] = Field(default_factory=lambda: [ImageScalingProperties()])


class Image(BaseVisual):
    visualType: str = "image"

    drillFilterOtherVisuals: bool = True
    objects: ImageProperties = Field(default_factory=ImageProperties)
