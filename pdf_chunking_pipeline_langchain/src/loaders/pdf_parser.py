from pathlib import Path

import pymupdf4llm
from langchain_core.documents import Document


def _resolve_page_number(
    parser_metadata: dict,
    page_index: int,
) -> int:
    """
    Resolve a stable 1-based PDF page number.

    PyMuPDF4LLM metadata can vary by version, so:
    1. use parser-provided page number when available
    2. otherwise fall back to page_index + 1
    """

    candidate_keys = (
        "page_number",
        "page",
        "pno",
    )

    for key in candidate_keys:
        value = parser_metadata.get(key)

        if isinstance(value, int):
            # Some parser metadata may be 0-based.
            if value == page_index:
                return page_index + 1

            # Already looks 1-based.
            if value == page_index + 1:
                return value

    return page_index + 1


def parse_pdf_to_documents(
    pdf_path: Path,
) -> list[Document]:
    """
    Parse the complete PDF with PyMuPDF4LLM and return
    one LangChain Document per PDF page.

    Design:
    - whole-document parsing in one call
    - page_chunks=True for page provenance
    - Markdown retained
    - parser controls reading order
    - no manual block sorting
    - no page-by-page parser calls
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"PDF path is not a file: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected PDF file: {pdf_path}"
        )

    print(
        f"Parsing PDF: {pdf_path}"
    )

    page_chunks = pymupdf4llm.to_markdown(
        str(pdf_path),
        page_chunks=True,
        write_images=False,
        embed_images=False,
        ignore_images=True,
        force_text=True,
        show_progress=True,
    )

    if not isinstance(page_chunks, list):
        raise TypeError(
            "Expected PyMuPDF4LLM to return a list "
            "because page_chunks=True."
        )

    documents = []

    for page_index, page_chunk in enumerate(
        page_chunks
    ):
        if not isinstance(page_chunk, dict):
            raise TypeError(
                "Expected each page chunk to be a dict. "
                f"Got: {type(page_chunk).__name__}"
            )

        text = (
            page_chunk.get("text", "")
            or ""
        ).strip()

        parser_metadata = (
            page_chunk.get("metadata", {})
            or {}
        )

        if not isinstance(parser_metadata, dict):
            parser_metadata = {}

        page_number = _resolve_page_number(
            parser_metadata=parser_metadata,
            page_index=page_index,
        )

        metadata = {
            "source": str(pdf_path),
            "source_name": pdf_path.name,
            "page_number": page_number,
            "page_index": page_index,
            "content_type": "parsed_page",
            "parser": "pymupdf4llm",
        }

        documents.append(
            Document(
                page_content=text,
                metadata=metadata,
            )
        )

    print(
        f"\nParsed page Documents: "
        f"{len(documents)}"
    )

    return documents

