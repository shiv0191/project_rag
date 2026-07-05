import re
from collections import Counter
from pathlib import Path

import fitz
from langchain_core.documents import Document

from loaders.layout_models import LayoutLine


# ============================================================
# Configuration
# ============================================================

TOP_MARGIN_RATIO = 0.075
BOTTOM_MARGIN_RATIO = 0.075

COLUMN_GUTTER_RATIO = 0.025
FULL_WIDTH_RATIO = 0.68
CENTER_TOLERANCE_RATIO = 0.025

Y_TOLERANCE = 3.0

HEADING_MAX_WORDS = 24

# Maximum vertical distance for caption continuation.
CAPTION_CONTINUATION_GAP = 18.0


# ============================================================
# Patterns
# ============================================================

FIGURE_PATTERN = re.compile(
    r"^\s*(FIGURE|FIG\.)\s+\d+",
    re.IGNORECASE,
)

TABLE_PATTERN = re.compile(
    r"^\s*TABLE\s+\d+",
    re.IGNORECASE,
)

SECTION_PATTERN = re.compile(
    r"^\s*(?:\d+\.)+(?:\d+)?\s+.+"
)

SPACED_JACC_PATTERN = re.compile(
    r"^\s*J\s+A\s+C\s+C\s*$",
    re.IGNORECASE,
)

E_PAGE_PATTERN = re.compile(
    r"^\s*e\s*\d+\s*$",
    re.IGNORECASE,
)

GUIDELINE_PATTERN = re.compile(
    r"^\s*2026\s+AHA/ACC/ADA/ASN\s+CKM\s+Guideline\s*$",
    re.IGNORECASE,
)

NDUMELE_PATTERN = re.compile(
    r"^\s*Ndumele\s+et\s+al\s*$",
    re.IGNORECASE,
)

VOLUME_PATTERN = re.compile(
    r"J\s*A\s*C\s*C\s+V\s*O\s*L",
    re.IGNORECASE,
)

# Handles:
# J U N E 9 , 2 0 2 6 : e 1 8 8 9 – e 2 0 0 7
SPACED_DATE_FOOTER_PATTERN = re.compile(
    r"^\s*"
    r"J\s*U\s*N\s*E"
    r".*?"
    r"2\s*0\s*2\s*6"
    r".*?"
    r"e\s*\d"
    r".*$",
    re.IGNORECASE,
)

# Generic spaced journal footer containing e-page range.
SPACED_EPAGE_RANGE_PATTERN = re.compile(
    r"^\s*"
    r"(?:[A-Z]\s*){3,}"
    r".*?"
    r"e\s*\d(?:\s*\d)+"
    r"\s*[–—-]\s*"
    r"e\s*\d(?:\s*\d)+"
    r"\s*$",
    re.IGNORECASE,
)


# ============================================================
# Low-level extraction
# ============================================================

def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


def span_is_bold(span: dict) -> bool:
    font_name = (
        span.get("font", "")
        or ""
    ).lower()

    flags = span.get("flags", 0)

    return (
        "bold" in font_name
        or bool(flags & 16)
    )


def extract_layout_lines(
    page: fitz.Page,
    page_number: int,
) -> list[LayoutLine]:

    page_dict = page.get_text(
        "dict",
        sort=False,
    )

    page_width = float(
        page.rect.width
    )

    page_height = float(
        page.rect.height
    )

    results = []

    for block_index, block in enumerate(
        page_dict.get("blocks", [])
    ):
        if block.get("type") != 0:
            continue

        for line_index, line in enumerate(
            block.get("lines", [])
        ):
            spans = line.get(
                "spans",
                [],
            )

            if not spans:
                continue

            text = normalize_text(
                "".join(
                    span.get("text", "")
                    for span in spans
                )
            )

            if not text:
                continue

            bbox = line.get("bbox")

            if not bbox:
                continue

            x0, y0, x1, y1 = map(
                float,
                bbox,
            )

            font_names = tuple(
                sorted(
                    {
                        span.get("font", "")
                        for span in spans
                        if span.get("font")
                    }
                )
            )

            font_sizes = tuple(
                float(
                    span.get(
                        "size",
                        0.0,
                    )
                )
                for span in spans
                if span.get("size")
                is not None
            )

            is_bold = any(
                span_is_bold(span)
                for span in spans
            )

            results.append(
                LayoutLine(
                    text=text,
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    page_number=page_number,
                    page_width=page_width,
                    page_height=page_height,
                    font_names=font_names,
                    font_sizes=font_sizes,
                    is_bold=is_bold,
                    source_block_index=(
                        block_index
                    ),
                    source_line_index=(
                        line_index
                    ),
                )
            )

    return results


# ============================================================
# Furniture detection
# ============================================================

def is_running_furniture(
    line: LayoutLine,
) -> bool:

    text = line.text.strip()

    top_limit = (
        line.page_height
        * TOP_MARGIN_RATIO
    )

    bottom_limit = (
        line.page_height
        * (
            1.0
            - BOTTOM_MARGIN_RATIO
        )
    )

    near_top = (
        line.y0 <= top_limit
    )

    near_bottom = (
        line.y1 >= bottom_limit
    )

    known_pattern = any(
        pattern.search(text)
        for pattern in [
            SPACED_JACC_PATTERN,
            E_PAGE_PATTERN,
            GUIDELINE_PATTERN,
            NDUMELE_PATTERN,
            VOLUME_PATTERN,
            SPACED_DATE_FOOTER_PATTERN,
            SPACED_EPAGE_RANGE_PATTERN,
        ]
    )

    if (
        known_pattern
        and (
            near_top
            or near_bottom
        )
    ):
        return True

    lower = text.lower()

    if (
        "ndumele et al" in lower
        and "ckm guideline" in lower
        and (
            near_top
            or near_bottom
        )
    ):
        return True

    return False


# ============================================================
# Content classification
# ============================================================

def median_font_size(
    lines: list[LayoutLine],
) -> float:

    sizes = []

    for line in lines:
        sizes.extend(
            size
            for size in line.font_sizes
            if size > 0
        )

    if not sizes:
        return 0.0

    sizes.sort()

    middle = len(sizes) // 2

    if len(sizes) % 2:
        return sizes[middle]

    return (
        sizes[middle - 1]
        + sizes[middle]
    ) / 2.0


def looks_like_heading(
    line: LayoutLine,
    body_font_size: float,
) -> bool:

    text = line.text.strip()

    if not text:
        return False

    if FIGURE_PATTERN.match(text):
        return False

    if TABLE_PATTERN.match(text):
        return False

    if SECTION_PATTERN.match(text):
        return True

    words = text.split()

    if len(words) > HEADING_MAX_WORDS:
        return False

    max_size = max(
        line.font_sizes,
        default=0.0,
    )

    larger_than_body = (
        body_font_size > 0
        and max_size
        >= body_font_size * 1.18
    )

    return (
        line.is_bold
        and larger_than_body
    )


def classify_content_types(
    lines: list[LayoutLine],
) -> None:

    body_size = median_font_size(
        lines
    )

    for line in lines:
        if is_running_furniture(line):
            line.content_type = (
                "furniture"
            )

        elif FIGURE_PATTERN.match(
            line.text
        ):
            line.content_type = (
                "figure_caption"
            )

        elif TABLE_PATTERN.match(
            line.text
        ):
            line.content_type = (
                "table"
            )

        elif looks_like_heading(
            line,
            body_size,
        ):
            line.content_type = (
                "heading"
            )

        else:
            line.content_type = "body"


# ============================================================
# Column classification
# ============================================================

def classify_regions(
    lines: list[LayoutLine],
) -> None:

    if not lines:
        return

    page_width = (
        lines[0].page_width
    )

    center_x = (
        page_width / 2.0
    )

    gutter_half = (
        page_width
        * COLUMN_GUTTER_RATIO
    )

    center_tolerance = (
        page_width
        * CENTER_TOLERANCE_RATIO
    )

    left_boundary = (
        center_x - gutter_half
    )

    right_boundary = (
        center_x + gutter_half
    )

    for line in lines:
        width_ratio = (
            line.width / page_width
        )

        crosses_center = (
            line.x0
            < center_x
            - center_tolerance
            and line.x1
            > center_x
            + center_tolerance
        )

        if (
            width_ratio
            >= FULL_WIDTH_RATIO
            and crosses_center
        ):
            line.region = "full_width"

        elif line.x1 <= right_boundary:
            line.region = "left"

        elif line.x0 >= left_boundary:
            line.region = "right"

        elif line.center_x < center_x:
            line.region = "left"

        elif line.center_x > center_x:
            line.region = "right"

        else:
            line.region = "unknown"


# ============================================================
# Reading order
# ============================================================

def sort_column_lines(
    lines: list[LayoutLine],
) -> list[LayoutLine]:

    return sorted(
        lines,
        key=lambda line: (
            round(
                line.y0
                / Y_TOLERANCE
            ),
            line.x0,
            (
                line.source_block_index
                or 0
            ),
            (
                line.source_line_index
                or 0
            ),
        ),
    )


def sort_full_width_lines(
    lines: list[LayoutLine],
) -> list[LayoutLine]:

    return sorted(
        lines,
        key=lambda line: (
            line.y0,
            line.x0,
        ),
    )


def build_vertical_bands(
    lines: list[LayoutLine],
) -> list[list[LayoutLine]]:

    content_lines = [
        line
        for line in lines
        if line.content_type
        != "furniture"
    ]

    if not content_lines:
        return []

    boundary_lines = sorted(
        [
            line
            for line in content_lines
            if (
                line.region
                == "full_width"
                and line.content_type
                in {
                    "heading",
                    "table",
                    "figure_caption",
                }
            )
        ],
        key=lambda line: line.y0,
    )

    if not boundary_lines:
        return [content_lines]

    bands = []

    current_top = 0.0

    for boundary in boundary_lines:
        before = [
            line
            for line in content_lines
            if (
                line.y0 >= current_top
                and line.y0
                < boundary.y0
                and line is not boundary
            )
        ]

        if before:
            bands.append(before)

        bands.append([boundary])

        current_top = max(
            current_top,
            boundary.y1,
        )

    after = [
        line
        for line in content_lines
        if line.y0 >= current_top
    ]

    if after:
        bands.append(after)

    return bands


def order_band(
    band: list[LayoutLine],
) -> list[LayoutLine]:

    if len(band) == 1:
        return band

    full_width = [
        line
        for line in band
        if line.region == "full_width"
    ]

    left = [
        line
        for line in band
        if line.region == "left"
    ]

    right = [
        line
        for line in band
        if line.region == "right"
    ]

    unknown = [
        line
        for line in band
        if line.region == "unknown"
    ]

    ordered = []

    top_of_columns = min(
        [
            line.y0
            for line in left + right
        ],
        default=float("inf"),
    )

    upper_full_width = [
        line
        for line in full_width
        if line.y1 <= top_of_columns
    ]

    remaining_full_width = [
        line
        for line in full_width
        if line
        not in upper_full_width
    ]

    ordered.extend(
        sort_full_width_lines(
            upper_full_width
        )
    )

    ordered.extend(
        sort_column_lines(left)
    )

    ordered.extend(
        sort_column_lines(right)
    )

    ordered.extend(
        sort_full_width_lines(
            remaining_full_width
        )
    )

    ordered.extend(
        sorted(
            unknown,
            key=lambda line: (
                line.y0,
                line.x0,
            ),
        )
    )

    return ordered


def reconstruct_page_order(
    lines: list[LayoutLine],
) -> list[LayoutLine]:

    bands = build_vertical_bands(
        lines
    )

    ordered = []

    for band in bands:
        ordered.extend(
            order_band(band)
        )

    return ordered


# ============================================================
# Text reconstruction
# ============================================================

def should_dehyphenate(
    previous: str,
    current: str,
) -> bool:

    if not previous.endswith("-"):
        return False

    if not current:
        return False

    if not current[0].islower():
        return False

    if re.search(
        r"\d-$",
        previous,
    ):
        return False

    return True


def join_lines(
    lines: list[LayoutLine],
) -> str:

    if not lines:
        return ""

    parts = []

    for line in lines:
        text = line.text.strip()

        if not text:
            continue

        if not parts:
            parts.append(text)
            continue

        previous = parts[-1]

        if should_dehyphenate(
            previous,
            text,
        ):
            parts[-1] = (
                previous[:-1]
                + text
            )
            continue

        if line.content_type in {
            "heading",
            "figure_caption",
            "table",
        }:
            parts.append(
                "\n\n" + text
            )
            continue

        parts.append(
            " " + text
        )

    return "".join(parts).strip()


# ============================================================
# Atomic content separation
# ============================================================

def same_caption_region(
    anchor: LayoutLine,
    candidate: LayoutLine,
) -> bool:
    """
    Decide whether candidate is a continuation of an explicit
    FIGURE/TABLE caption.

    Critical property:
    capture is bounded by geometry. It does not remain active
    until some future heading.
    """

    vertical_gap = (
        candidate.y0 - anchor.y1
    )

    if vertical_gap < -2.0:
        return False

    if (
        vertical_gap
        > CAPTION_CONTINUATION_GAP
    ):
        return False

    # Same column / same full-width region.
    if candidate.region == anchor.region:
        return True

    # Allow strong horizontal overlap.
    overlap = max(
        0.0,
        min(
            anchor.x1,
            candidate.x1,
        )
        - max(
            anchor.x0,
            candidate.x0,
        ),
    )

    candidate_width = max(
        candidate.width,
        1.0,
    )

    overlap_ratio = (
        overlap / candidate_width
    )

    return overlap_ratio >= 0.60


def collect_atomic_indices(
    ordered_lines: list[LayoutLine],
    start_index: int,
) -> set[int]:
    """
    Collect only geometrically adjacent continuation lines.

    This replaces the previous open-ended active_atomic_type
    state machine.
    """

    indices = {
        start_index
    }

    anchor = ordered_lines[
        start_index
    ]

    previous = anchor

    for index in range(
        start_index + 1,
        len(ordered_lines),
    ):
        candidate = ordered_lines[
            index
        ]

        if candidate.content_type in {
            "heading",
            "figure_caption",
            "table",
        }:
            break

        if not same_caption_region(
            previous,
            candidate,
        ):
            break

        indices.add(index)

        previous = candidate

    return indices


def split_atomic_content(
    ordered_lines: list[LayoutLine],
) -> tuple[
    list[LayoutLine],
    list[LayoutLine],
    list[LayoutLine],
]:
    """
    Separate body, figure captions, and table material.

    Unlike the previous implementation, FIGURE/TABLE markers
    do not swallow the remainder of the page.
    """

    figure_indices = set()
    table_indices = set()

    for index, line in enumerate(
        ordered_lines
    ):
        if (
            line.content_type
            == "figure_caption"
        ):
            figure_indices.update(
                collect_atomic_indices(
                    ordered_lines,
                    index,
                )
            )

        elif (
            line.content_type
            == "table"
        ):
            table_indices.update(
                collect_atomic_indices(
                    ordered_lines,
                    index,
                )
            )

    # Explicit figure wins if an accidental overlap occurs.
    table_indices -= figure_indices

    body_lines = []
    figure_lines = []
    table_lines = []

    for index, line in enumerate(
        ordered_lines
    ):
        if index in figure_indices:
            figure_lines.append(line)

        elif index in table_indices:
            table_lines.append(line)

        else:
            body_lines.append(line)

    return (
        body_lines,
        figure_lines,
        table_lines,
    )


# ============================================================
# Public parser
# ============================================================

def parse_pdf_to_documents(
    pdf_path: Path,
) -> list[Document]:

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    pdf = fitz.open(pdf_path)

    documents = []

    try:
        for page_index in range(
            len(pdf)
        ):
            page = pdf[page_index]

            page_number = (
                page_index + 1
            )

            lines = extract_layout_lines(
                page,
                page_number,
            )

            classify_content_types(
                lines
            )

            classify_regions(
                lines
            )

            ordered_lines = (
                reconstruct_page_order(
                    lines
                )
            )

            (
                body_lines,
                figure_lines,
                table_lines,
            ) = split_atomic_content(
                ordered_lines
            )

            body_text = join_lines(
                body_lines
            )

            if body_text:
                documents.append(
                    Document(
                        page_content=(
                            body_text
                        ),
                        metadata={
                            "source": str(
                                pdf_path
                            ),
                            "source_name": (
                                pdf_path.name
                            ),
                            "page_number": (
                                page_number
                            ),
                            "page_index": (
                                page_index
                            ),
                            "content_type": (
                                "page_body"
                            ),
                            "parser": (
                                "pymupdf_layout"
                            ),
                        },
                    )
                )

            figure_text = join_lines(
                figure_lines
            )

            if figure_text:
                documents.append(
                    Document(
                        page_content=(
                            figure_text
                        ),
                        metadata={
                            "source": str(
                                pdf_path
                            ),
                            "source_name": (
                                pdf_path.name
                            ),
                            "page_number": (
                                page_number
                            ),
                            "page_index": (
                                page_index
                            ),
                            "content_type": (
                                "figure_caption"
                            ),
                            "parser": (
                                "pymupdf_layout"
                            ),
                        },
                    )
                )

            table_text = join_lines(
                table_lines
            )

            if table_text:
                documents.append(
                    Document(
                        page_content=(
                            table_text
                        ),
                        metadata={
                            "source": str(
                                pdf_path
                            ),
                            "source_name": (
                                pdf_path.name
                            ),
                            "page_number": (
                                page_number
                            ),
                            "page_index": (
                                page_index
                            ),
                            "content_type": (
                                "table"
                            ),
                            "parser": (
                                "pymupdf_layout"
                            ),
                        },
                    )
                )

    finally:
        pdf.close()

    return documents


def summarize_document_types(
    documents: list[Document],
) -> dict[str, int]:

    counter = Counter(
        document.metadata.get(
            "content_type",
            "unknown",
        )
        for document in documents
    )

    return dict(counter)

