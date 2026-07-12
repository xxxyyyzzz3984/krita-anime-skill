"""Strict, model-neutral schema for editable anime scenes."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Color = Annotated[str, Field(pattern=r"^(#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{8}|none)$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Canvas(StrictModel):
    width: Annotated[int, Field(ge=64, le=8192)]
    height: Annotated[int, Field(ge=64, le=8192)]
    name: Annotated[str, Field(min_length=1, max_length=120)]
    background: Color = "#FFFFFF"


class Point(StrictModel):
    x: float
    y: float


class PressurePoint(Point):
    pressure: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0


class CharacterAnchors(StrictModel):
    face: Annotated[str, Field(min_length=1)]
    eyes: Annotated[str, Field(min_length=1)]
    hair: Annotated[str, Field(min_length=1)]
    signature: Annotated[list[str], Field(min_length=1)]
    proportions: str = ""


class CharacterPack(StrictModel):
    id: Annotated[str, Field(pattern=r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$")]
    anchors: CharacterAnchors
    palette: dict[str, Color]
    default_costume: Annotated[str, Field(min_length=1)]
    allowed_variations: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class CharacterInstance(StrictModel):
    character_id: str
    pose: Annotated[str, Field(min_length=1)]
    expression: Annotated[str, Field(min_length=1)]
    costume: str | None = None
    scene_notes: str = ""


class BrushStroke(StrictModel):
    op: Literal["brush_stroke"]
    preset: Annotated[str, Field(min_length=1)]
    color: Color
    size: Annotated[float, Field(gt=0.0, le=1000.0)]
    opacity: Annotated[float, Field(gt=0.0, le=1.0)] = 1.0
    stabilizer: Annotated[float, Field(ge=0.0, le=1.0)] = 0.0
    points: Annotated[list[PressurePoint], Field(min_length=2, max_length=4096)]


class BezierSegment(StrictModel):
    control1: Point
    control2: Point
    end: Point


class BezierPath(StrictModel):
    op: Literal["bezier_path"]
    start: Point
    segments: Annotated[list[BezierSegment], Field(min_length=1, max_length=1024)]
    stroke: Color = "#000000"
    fill: Color = "none"
    stroke_width: Annotated[float, Field(gt=0.0, le=1000.0)] = 1.0
    closed: bool = False
    opacity: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0


class StoryboardPanel(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=64)]
    x: Annotated[int, Field(ge=0)]
    y: Annotated[int, Field(ge=0)]
    width: Annotated[int, Field(gt=0)]
    height: Annotated[int, Field(gt=0)]
    camera: str = "medium shot"
    action: Annotated[str, Field(min_length=1)]
    dialogue: str = ""
    notes: str = ""


class Storyboard(StrictModel):
    op: Literal["storyboard"]
    panels: Annotated[list[StoryboardPanel], Field(min_length=1, max_length=64)]
    gutter: Annotated[int, Field(ge=0, le=200)] = 24
    border_color: Color = "#202020"
    border_width: Annotated[float, Field(gt=0.0, le=50.0)] = 4.0


Operation = Annotated[BrushStroke | BezierPath | Storyboard, Field(discriminator="op")]
Phase = Literal["reference", "rough", "construction", "lineart", "flats", "shadows", "highlights", "effects", "notes"]


class AnimeLayer(StrictModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    phase: Phase
    kind: Literal["paint", "vector", "storyboard"]
    opacity: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    visible: bool = True
    operations: Annotated[list[Operation], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_operations_match_layer(self) -> AnimeLayer:
        if self.kind == "paint" and any(not isinstance(op, BrushStroke) for op in self.operations):
            message = "paint layers only accept brush_stroke operations"
            raise ValueError(message)
        if self.kind == "vector" and any(not isinstance(op, BezierPath) for op in self.operations):
            message = "vector layers only accept bezier_path operations"
            raise ValueError(message)
        if self.kind == "storyboard" and any(not isinstance(op, Storyboard) for op in self.operations):
            message = "storyboard layers only accept storyboard operations"
            raise ValueError(message)
        return self


class ExportTarget(StrictModel):
    path: Annotated[str, Field(min_length=1)]
    format: Literal["kra", "png", "jpg", "webp"]

    @field_validator("path")
    @classmethod
    def reject_parent_traversal(cls, value: str) -> str:
        normalized = value.replace("\\", "/")
        if ".." in normalized.split("/"):
            message = "export path cannot contain parent traversal"
            raise ValueError(message)
        return value


class AnimePlan(StrictModel):
    version: Literal["1.0"]
    canvas: Canvas
    characters: list[CharacterPack] = Field(default_factory=list)
    cast: list[CharacterInstance] = Field(default_factory=list)
    layers: Annotated[list[AnimeLayer], Field(min_length=1, max_length=100)]
    exports: Annotated[list[ExportTarget], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def validate_scene(self) -> AnimePlan:
        character_ids = [character.id for character in self.characters]
        if len(character_ids) != len(set(character_ids)):
            message = "character ids must be unique"
            raise ValueError(message)
        known = set(character_ids)
        for instance in self.cast:
            if instance.character_id not in known:
                message = f"unknown character reference: {instance.character_id}"
                raise ValueError(message)
        operation_count = sum(len(layer.operations) for layer in self.layers)
        if operation_count > 2000:
            message = "plan cannot contain more than 2000 operations"
            raise ValueError(message)
        for layer in self.layers:
            for operation in layer.operations:
                if isinstance(operation, Storyboard):
                    for panel in operation.panels:
                        if panel.x + panel.width > self.canvas.width or panel.y + panel.height > self.canvas.height:
                            message = f"storyboard panel {panel.id} exceeds the canvas"
                            raise ValueError(message)
        return self
