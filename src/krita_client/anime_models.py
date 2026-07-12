"""Typed request models for fine-grained anime plugin actions."""

from __future__ import annotations

from typing import Annotated
from xml.etree import ElementTree as ET

from pydantic import BaseModel, Field, field_validator


class NativeStrokePoint(BaseModel):
    x: float
    y: float
    pressure: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0


class NativeStrokeParams(BaseModel):
    points: Annotated[list[NativeStrokePoint], Field(min_length=2, max_length=4096)]
    preset: Annotated[str, Field(min_length=1)]
    size: Annotated[float, Field(gt=0.0, le=1000.0)]
    opacity: Annotated[float, Field(gt=0.0, le=1.0)] = 1.0


class ImportSvgLayerParams(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    svg: Annotated[str, Field(min_length=11, max_length=2_000_000)]
    opacity: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    visible: bool = True

    @field_validator("svg")
    @classmethod
    def secure_svg(cls, value: str) -> str:
        try:
            root = ET.fromstring(value)  # noqa: S314 - bounded input; stdlib parser does not resolve external entities
        except ET.ParseError as error:
            message = "SVG must be well-formed XML"
            raise ValueError(message) from error
        if root.tag.rsplit("}", 1)[-1].lower() != "svg":
            message = "SVG must be inline and cannot contain scripts or external resources"
            raise ValueError(message)
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1].lower() == "script":
                message = "SVG must be inline and cannot contain scripts or external resources"
                raise ValueError(message)
            for attribute, raw_value in element.attrib.items():
                name = attribute.rsplit("}", 1)[-1].lower()
                lowered = raw_value.strip().lower()
                has_external_scheme = any(
                    scheme in lowered for scheme in ("javascript:", "file://", "http://", "https://")
                )
                if name.startswith("on") or has_external_scheme or (name == "href" and not lowered.startswith("#")):
                    message = "SVG must be inline and cannot contain scripts or external resources"
                    raise ValueError(message)
        return value


class StoryboardPanelParams(BaseModel):
    id: str
    x: Annotated[int, Field(ge=0)]
    y: Annotated[int, Field(ge=0)]
    width: Annotated[int, Field(gt=0)]
    height: Annotated[int, Field(gt=0)]
    camera: str = "medium shot"
    action: Annotated[str, Field(min_length=1)]
    dialogue: str = ""
    notes: str = ""


class CreateStoryboardParams(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    panels: Annotated[list[StoryboardPanelParams], Field(min_length=1, max_length=64)]
    gutter: Annotated[int, Field(ge=0, le=200)] = 24
    border_color: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")] = "#202020"
    border_width: Annotated[float, Field(gt=0.0, le=50.0)] = 4.0


ANIME_COMMAND_MODELS: dict[str, type[BaseModel]] = {
    "native_stroke": NativeStrokeParams,
    "import_svg_layer": ImportSvgLayerParams,
    "create_storyboard": CreateStoryboardParams,
}
