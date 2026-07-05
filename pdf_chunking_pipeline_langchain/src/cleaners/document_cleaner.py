import re

from langchain_core.documents import Document


# ============================================================
# Known running-furniture patterns
# ============================================================

RUNNING_FURNITURE_PATTERNS = [
    # --------------------------------------------------------
    # Spaced journal header:
    #
    # J A C C V O L . 8 7 , N O . 2 2 S , 2 0 2 6
    # J U N E 9 , 2 0 2 6 : e 1 8 8 9 – e 2 0 0 7
    #
    # Can appear as one combined line.
    # --------------------------------------------------------
    re.compile(
        r"^\s*"
        r"J\s+A\s+C\s+C\s+"
        r"V\s+O\s+L\s*\.\s*"
        r".*?"
        r"J\s+U\s+N\s+E\s+"
        r".*?"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Standalone spaced JACC volume header
    # --------------------------------------------------------
    re.compile(
        r"^\s*"
        r"J\s+A\s+C\s+C\s+"
        r"V\s+O\s+L\s*\.\s*"
        r".*"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Standalone spaced journal name:
    #
    # J A C C
    # --------------------------------------------------------
    re.compile(
        r"^\s*"
        r"J\s+A\s+C\s+C"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Standalone spaced date/footer:
    #
    # J U N E 9 , 2 0 2 6 : e 1 8 8 9 – e 2 0 0 7
    # --------------------------------------------------------
    re.compile(
        r"^\s*"
        r"J\s+U\s+N\s+E\s+"
        r".*"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Combined form:
    #
    # > e1890 Ndumele et al
    #   2026 AHA/ACC/ADA/ASN CKM Guideline
    #
    # when parser places everything on one line
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"e\d+\s+"
        r"Ndumele et al\s+"
        r"2026 AHA/ACC/ADA/ASN CKM Guideline"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Combined form:
    #
    # Ndumele et al e1891
    # 2026 AHA/ACC/ADA/ASN CKM Guideline
    #
    # when parser places everything on one line
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"Ndumele et al\s+"
        r"e\d+\s+"
        r"2026 AHA/ACC/ADA/ASN CKM Guideline"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Combined form:
    #
    # Ndumele et al
    # 2026 AHA/ACC/ADA/ASN CKM Guideline
    # e1891
    #
    # when parser places everything on one line
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"Ndumele et al\s+"
        r"2026 AHA/ACC/ADA/ASN CKM Guideline\s+"
        r"e\d+"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Combined form without article page:
    #
    # Ndumele et al
    # 2026 AHA/ACC/ADA/ASN CKM Guideline
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"Ndumele et al\s+"
        r"2026 AHA/ACC/ADA/ASN CKM Guideline"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Standalone author furniture:
    #
    # Ndumele et al
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"Ndumele et al"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Standalone article page:
    #
    # e1891
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"e\d+"
        r"\s*$",
        re.IGNORECASE,
    ),

    # --------------------------------------------------------
    # Standalone short guideline title
    # --------------------------------------------------------
    re.compile(
        r"^\s*>?\s*"
        r"2026 AHA/ACC/ADA/ASN CKM Guideline"
        r"\s*$",
        re.IGNORECASE,
    ),
]


# ============================================================
# Furniture detection
# ============================================================

def is_running_furniture(
    line: str,
) -> bool:
    """
    Return True only when the complete line matches
    known publication running furniture.

    Important:
    - full-line matching only
    - no substring deletion
    - conservative by design
    """

    stripped = line.strip()

    if not stripped:
        return False

    return any(
        pattern.fullmatch(stripped)
        for pattern in RUNNING_FURNITURE_PATTERNS
    )


# ============================================================
# Single-document cleaning
# ============================================================

def clean_document(
    document: Document,
) -> Document:
    """
    Remove known running furniture from one LangChain
    Document while preserving all source metadata.

    Adds:
    - original_character_count
    - cleaned_character_count
    - removed_furniture_lines
    """

    original_text = document.page_content

    kept_lines = []
    removed_lines = []

    for line in original_text.splitlines():
        if is_running_furniture(line):
            removed_lines.append(line)
            continue

        kept_lines.append(line)

    cleaned_text = "\n".join(
        kept_lines
    ).strip()

    metadata = dict(document.metadata)

    metadata.update(
        {
            "original_character_count":
                len(original_text),

            "cleaned_character_count":
                len(cleaned_text),

            "removed_furniture_lines":
                len(removed_lines),
        }
    )

    return Document(
        page_content=cleaned_text,
        metadata=metadata,
    )


# ============================================================
# Corpus cleaning
# ============================================================

def clean_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Clean all page Documents.

    Page count and page provenance are preserved.
    """

    cleaned_documents = []

    for document in documents:
        cleaned_documents.append(
            clean_document(document)
        )

    return cleaned_documents
