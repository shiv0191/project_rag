from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
)


HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
]

HEADER_KEYS = [
    "h1",
    "h2",
    "h3",
    "h4",
]


def normalize_heading(value: str | None) -> str:
    """
    Normalize heading text for control-flow comparisons only.

    Original heading text is still preserved in metadata.
    """

    if not value:
        return ""

    return (
        value
        .replace("*", "")
        .strip()
        .upper()
    )


def is_table_of_contents_heading(
    value: str | None,
) -> bool:
    return (
        normalize_heading(value)
        == "TABLE OF CONTENTS"
    )


def starts_real_content_after_toc(
    detected_headings: dict,
) -> bool:
    """
    Detect the first known real-content heading after
    the table of contents.

    In this PDF, TOP TAKE-HOME MESSAGES marks the
    transition from TOC material to actual document
    content.

    This is intentionally narrow. We do not treat every
    h3/h4 as a TOC exit because APPENDIX headings can
    appear inside the TOC itself.
    """

    for key in HEADER_KEYS:
        value = detected_headings.get(key)

        if (
            normalize_heading(value)
            == "TOP TAKE-HOME MESSAGES"
        ):
            return True

    return False


def apply_detected_headings(
    active_headings: dict,
    detected_headings: dict,
) -> dict:
    """
    Apply headings detected in the current section.

    If a heading changes at level N, all headings at
    level N and deeper are cleared before current
    headings are applied.
    """

    updated = dict(active_headings)

    detected_levels = [
        index
        for index, key in enumerate(HEADER_KEYS)
        if key in detected_headings
    ]

    if detected_levels:
        highest_changed_level = min(
            detected_levels
        )

        for key in HEADER_KEYS[
            highest_changed_level:
        ]:
            updated.pop(key, None)

    for key in HEADER_KEYS:
        if key in detected_headings:
            updated[key] = detected_headings[key]

    return updated


def split_markdown_by_headers(
    documents: list[Document],
) -> list[Document]:
    """
    Split cleaned page Documents while preserving:

    - exact page provenance
    - source metadata
    - heading hierarchy
    - cross-page heading context

    Also prevents TABLE OF CONTENTS metadata from
    leaking into real document sections.
    """

    if not documents:
        return []

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )

    results = []
    active_headings = {}
    structural_index = 0

    for page_document in documents:
        page_sections = splitter.split_text(
            page_document.page_content
        )

        for section in page_sections:
            detected_headings = {
                key: value
                for key, value
                in section.metadata.items()
                if key in HEADER_KEYS
            }

            # -------------------------------------------------
            # Explicit TOC -> real-content boundary
            # -------------------------------------------------
            if (
                is_table_of_contents_heading(
                    active_headings.get("h2")
                )
                and starts_real_content_after_toc(
                    detected_headings
                )
            ):
                active_headings.pop("h2", None)
                active_headings.pop("h3", None)
                active_headings.pop("h4", None)

            effective_headings = (
                apply_detected_headings(
                    active_headings,
                    detected_headings,
                )
            )

            metadata = dict(effective_headings)

            metadata.update(
                {
                    "structural_index":
                        structural_index,

                    "source":
                        page_document.metadata.get(
                            "source"
                        ),

                    "source_name":
                        page_document.metadata.get(
                            "source_name"
                        ),

                    "content_type":
                        "markdown_section",

                    "page_number":
                        page_document.metadata.get(
                            "page_number"
                        ),

                    "page_index":
                        page_document.metadata.get(
                            "page_index"
                        ),
                }
            )

            text = section.page_content.strip()

            if text:
                results.append(
                    Document(
                        page_content=text,
                        metadata=metadata,
                    )
                )

                structural_index += 1

            active_headings = effective_headings

    return results

