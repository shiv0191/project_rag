from dataclasses import dataclass, field
from typing import Literal


RegionType = Literal[
    "left",
    "right",
    "full_width",
    "unknown",
]

ContentType = Literal[
    "body",
    "heading",
    "figure_caption",
    "table",
    "furniture",
    "unknown",
]


@dataclass
class LayoutLine:
    text: str

    x0: float
    y0: float
    x1: float
    y1: float

    page_number: int
    page_width: float
    page_height: float

    font_names: tuple[str, ...] = field(
        default_factory=tuple
    )
    font_sizes: tuple[float, ...] = field(
        default_factory=tuple
    )

    is_bold: bool = False

    region: RegionType = "unknown"
    content_type: ContentType = "unknown"

    source_block_index: int | None = None
    source_line_index: int | None = None

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2.0


@dataclass
class LayoutRegion:
    page_number: int
    region_type: RegionType
    content_type: ContentType

    lines: list[LayoutLine]

    @property
    def x0(self) -> float:
        return min(
            line.x0
            for line in self.lines
        )

    @property
    def y0(self) -> float:
        return min(
            line.y0
            for line in self.lines
        )

    @property
    def x1(self) -> float:
        return max(
            line.x1
            for line in self.lines
        )

    @property
    def y1(self) -> float:
        return max(
            line.y1
            for line in self.lines
        )

    @property
    def text(self) -> str:
        return "\n".join(
            line.text
            for line in self.lines
        )
