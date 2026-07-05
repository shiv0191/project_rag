import re

from langchain_core.documents import Document


# ---------------------------------------------------------
# Front-matter / non-retrieval section rules
# ---------------------------------------------------------

NON_RETRIEVAL_H2 = {
    "TABLE OF CONTENTS",
}


def normalize_heading(value: str | None) -> str:
    """
    Normalize Markdown heading metadata.

    Examples:
        "**TABLE OF CONTENTS**"
            -> "TABLE OF CONTENTS"

        "  Table of Contents  "
            -> "TABLE OF CONTENTS"
    """

    if not value:
        return ""

    text = value.strip()

    # Remove Markdown emphasis markers.
    text = re.sub(
        r"[*_`]+",
        "",
        text,
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip().upper()


# ---------------------------------------------------------
# Spaced publication boilerplate
# ---------------------------------------------------------

SPACED_VOLUME_PATTERN = re.compile(
    r"^\s*V\s+O\s+L\s*\.",
    re.IGNORECASE,
)

SPACED_COPYRIGHT_PATTERN = re.compile(
    r""
    r"(?:"
    r"ª\s*2\s*0\s*2\s*6"
    r"|"
    r"©\s*2\s*0\s*2\s*6"
    r")"
    r".*?"
    r"(?:"
    r"A\s+M\s+E\s+R\s+I\s+C\s+A\s+N"
    r")",
    re.IGNORECASE | re.DOTALL,
)

SPACED_ELSEVIER_PATTERN = re.compile(
    r"P\s+U\s+B\s+L\s+I\s+S\s+H\s+E\s+D"
    r"\s+B\s+Y\s+E\s+L\s+S\s+E\s+V\s+I\s+E\s+R",
    re.IGNORECASE,
)


def is_spaced_publication_boilerplate(
    text: str,
) -> bool:
    """
    Detect page-1 publication boilerplate such as:

        V O L . 8 7 , N O . ...
        ... P U B L I S H E D B Y E L S E V I E R
    """

    stripped = text.strip()

    if not stripped:
        return False

    if SPACED_VOLUME_PATTERN.search(stripped):
        return True

    if SPACED_COPYRIGHT_PATTERN.search(stripped):
        return True

    if SPACED_ELSEVIER_PATTERN.search(stripped):
        return True

    return False


# ---------------------------------------------------------
# TOC detection
# ---------------------------------------------------------

def is_table_of_contents_section(
    document: Document,
) -> bool:
    """
    Reject every structural document whose active h2
    hierarchy is TABLE OF CONTENTS.

    This removes all TOC child fragments too, including
    false h4 values such as APPENDIX 2 detected inside TOC.
    """

    h2 = normalize_heading(
        document.metadata.get("h2")
    )

    return h2 in NON_RETRIEVAL_H2


# ---------------------------------------------------------
# Main decision
# ---------------------------------------------------------

def get_exclusion_reason(
    document: Document,
) -> str | None:
    """
    Return exclusion reason for one structural document.

    None means keep the document.
    """

    text = document.page_content.strip()

    if not text:
        return "empty_structural_document"

    if is_spaced_publication_boilerplate(text):
        return "publication_boilerplate"

    if is_table_of_contents_section(document):
        return "table_of_contents"

    return None


def filter_structural_documents(
    documents: list[Document],
) -> tuple[
    list[Document],
    list[Document],
    dict,
]:
    """
    Separate retrieval-worthy structural documents from
    known non-retrieval material.

    Important:
    This runs BEFORE recursive retrieval chunking.
    """

    kept = []
    excluded = []

    reason_counts = {}

    for document in documents:
        reason = get_exclusion_reason(document)

        if reason is None:
            kept.append(document)
            continue

        metadata = dict(document.metadata)

        metadata["corpus_exclusion_reason"] = reason

        excluded_document = Document(
            page_content=document.page_content,
            metadata=metadata,
        )

        excluded.append(excluded_document)

        reason_counts[reason] = (
            reason_counts.get(reason, 0) + 1
        )

    report = {
        "input_structural_documents": len(documents),
        "kept_structural_documents": len(kept),
        "excluded_structural_documents": len(excluded),
        "exclusion_counts": reason_counts,
    }

    return kept, excluded, report

