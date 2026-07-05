import re
from collections import Counter

from langchain_core.documents import Document


HEADING_LINE_PATTERN = re.compile(
    r"^\s{0,3}#{1,6}\s+.+$"
)

RUNNING_FURNITURE_PATTERNS = [
    re.compile(
        r"^\s*>?\s*e\d+\s+Ndumele et al\s+"
        r"2026 AHA/ACC/ADA/ASN CKM Guideline\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*Ndumele et al\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*e\d+\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*2026 AHA/ACC/ADA/ASN CKM Guideline\s*$",
        re.IGNORECASE,
    ),
]


def is_heading_only(
    text: str,
) -> bool:
    """
    Return True when every non-empty line is a
    Markdown heading.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    return all(
        HEADING_LINE_PATTERN.match(line)
        for line in lines
    )


def is_furniture_line(
    line: str,
) -> bool:
    """
    Detect known residual publication furniture.
    """

    stripped = line.strip()

    if not stripped:
        return False

    return any(
        pattern.match(stripped)
        for pattern in RUNNING_FURNITURE_PATTERNS
    )


def is_furniture_only(
    text: str,
) -> bool:
    """
    Return True only when every non-empty line is
    recognized residual publication furniture.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    return all(
        is_furniture_line(line)
        for line in lines
    )


def is_meaningless_fragment(
    text: str,
) -> bool:
    """
    Reject tiny parser/splitter debris.

    Examples:
        "."
        ","
        "-"
        "1"
        "()"

    Important:
    This is intentionally conservative.

    It does NOT reject:
        "CKD"
        "Stage 1"
        "eGFR"
        "20%"
        "3.1"
        "A1C"
    """

    stripped = text.strip()

    if not stripped:
        return False

    # Meaningful alphabetic content is preserved.
    if any(
        character.isalpha()
        for character in stripped
    ):
        return False

    compact = re.sub(
        r"\s+",
        "",
        stripped,
    )

    # Only tiny non-alphabetic fragments are rejected.
    return len(compact) <= 3


def validate_chunk(
    chunk: Document,
) -> list[str]:
    """
    Return rejection reasons for one chunk.

    Empty list means accepted.
    """

    reasons = []

    text = chunk.page_content.strip()
    metadata = chunk.metadata

    if not text:
        reasons.append(
            "empty_text"
        )

    if metadata.get(
        "page_number"
    ) is None:
        reasons.append(
            "missing_page_metadata"
        )

    if metadata.get(
        "structural_index"
    ) is None:
        reasons.append(
            "missing_structural_metadata"
        )

    if is_heading_only(text):
        reasons.append(
            "heading_only"
        )

    if is_furniture_only(text):
        reasons.append(
            "furniture_only"
        )

    if is_meaningless_fragment(text):
        reasons.append(
            "meaningless_fragment"
        )

    return reasons


def validate_chunks(
    chunks: list[Document],
) -> tuple[
    list[Document],
    list[Document],
    dict,
]:
    """
    Split chunks into accepted and rejected corpora.

    Rejected chunks retain rejection reasons
    in metadata.
    """

    accepted = []
    rejected = []

    rejection_counter = Counter()

    for chunk in chunks:
        reasons = validate_chunk(
            chunk
        )

        if not reasons:
            accepted.append(
                chunk
            )
            continue

        metadata = dict(
            chunk.metadata
        )

        metadata[
            "rejection_reasons"
        ] = reasons

        rejected_chunk = Document(
            page_content=(
                chunk.page_content
            ),
            metadata=metadata,
        )

        rejected.append(
            rejected_chunk
        )

        rejection_counter.update(
            reasons
        )

    report = {
        "input_chunks": len(chunks),
        "accepted_chunks": len(accepted),
        "rejected_chunks": len(rejected),
        "rejection_counts": dict(
            rejection_counter
        ),
    }

    return (
        accepted,
        rejected,
        report,
    )
