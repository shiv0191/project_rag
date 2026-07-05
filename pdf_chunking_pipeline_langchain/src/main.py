import json
from pathlib import Path
from statistics import mean, median

from langchain_core.documents import Document

from cleaners.document_cleaner import (
    clean_documents,
)
from loaders.layout_pdf_parser import (
    parse_pdf_to_documents,
    summarize_document_types,
)
from splitters.markdown_splitter import (
    split_markdown_by_headers,
)
from splitters.recursive_splitter import (
    CHUNK_SIZE_TOKENS,
    split_structural_documents,
)
from validators.chunk_validator import (
    validate_chunks,
)


PDF_PATH = Path(
    "data/"
    "ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-"
    "for-the-prevention-detection-evaluation-and-management-of.pdf"
)

OUTPUT_DIR = Path("output")

FINAL_CHUNKS_PATH = (
    OUTPUT_DIR
    / "chunks_final.jsonl"
)

REJECTED_CHUNKS_PATH = (
    OUTPUT_DIR
    / "rejected_chunks.jsonl"
)

FIGURE_CAPTIONS_PATH = (
    OUTPUT_DIR
    / "figure_captions.jsonl"
)

TABLES_PATH = (
    OUTPUT_DIR
    / "tables.jsonl"
)

REPORT_PATH = (
    OUTPUT_DIR
    / "final_chunk_report.json"
)


def write_documents_jsonl(
    path: Path,
    documents: list[Document],
) -> None:
    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for document in documents:
            record = {
                "page_content": (
                    document.page_content
                ),
                "metadata": (
                    document.metadata
                ),
            }

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def assign_final_chunk_ids(
    chunks: list[Document],
) -> list[Document]:
    results = []

    for chunk_index, chunk in enumerate(
        chunks
    ):
        metadata = dict(
            chunk.metadata
        )

        metadata.update(
            {
                "chunk_index": (
                    chunk_index
                ),
                "chunk_id": (
                    f"chunk_{chunk_index:06d}"
                ),
            }
        )

        results.append(
            Document(
                page_content=(
                    chunk.page_content
                ),
                metadata=metadata,
            )
        )

    return results


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 1. Layout-aware parsing
    # ========================================================

    parsed_documents = (
        parse_pdf_to_documents(
            PDF_PATH
        )
    )

    type_summary = (
        summarize_document_types(
            parsed_documents
        )
    )

    body_documents = [
        document
        for document in parsed_documents
        if document.metadata.get(
            "content_type"
        )
        == "page_body"
    ]

    figure_documents = [
        document
        for document in parsed_documents
        if document.metadata.get(
            "content_type"
        )
        == "figure_caption"
    ]

    table_documents = [
        document
        for document in parsed_documents
        if document.metadata.get(
            "content_type"
        )
        == "table"
    ]

    # ========================================================
    # 2. Existing cleaner
    # ========================================================

    cleaned_documents = (
        clean_documents(
            body_documents
        )
    )

    # ========================================================
    # 3. Existing Markdown structural splitter
    # ========================================================

    structural_documents = (
        split_markdown_by_headers(
            cleaned_documents
        )
    )

    # ========================================================
    # 4. Existing recursive retrieval splitter
    # ========================================================

    candidate_chunks = (
        split_structural_documents(
            structural_documents
        )
    )

    # ========================================================
    # 5. Existing quality gate
    # ========================================================

    (
        accepted_chunks,
        rejected_chunks,
        validation_report,
    ) = validate_chunks(
        candidate_chunks
    )

    # ========================================================
    # 6. Final IDs
    # ========================================================

    final_chunks = (
        assign_final_chunk_ids(
            accepted_chunks
        )
    )

    # ========================================================
    # 7. Final validation
    # ========================================================

    missing_page_metadata = [
        chunk
        for chunk in final_chunks
        if chunk.metadata.get(
            "page_number"
        )
        is None
    ]

    missing_structural_metadata = [
        chunk
        for chunk in final_chunks
        if chunk.metadata.get(
            "structural_index"
        )
        is None
    ]

    empty_chunks = [
        chunk
        for chunk in final_chunks
        if not chunk.page_content.strip()
    ]

    over_limit = [
        chunk
        for chunk in final_chunks
        if chunk.metadata.get(
            "token_count",
            0,
        )
        > CHUNK_SIZE_TOKENS
    ]

    chunk_ids = [
        chunk.metadata["chunk_id"]
        for chunk in final_chunks
    ]

    duplicate_chunk_ids = (
        len(chunk_ids)
        != len(set(chunk_ids))
    )

    expected_indices = list(
        range(
            len(final_chunks)
        )
    )

    actual_indices = [
        chunk.metadata["chunk_index"]
        for chunk in final_chunks
    ]

    contiguous_indices = (
        actual_indices
        == expected_indices
    )

    token_counts = [
        chunk.metadata["token_count"]
        for chunk in final_chunks
    ]

    page_numbers = [
        chunk.metadata["page_number"]
        for chunk in final_chunks
        if chunk.metadata.get(
            "page_number"
        )
        is not None
    ]

    hard_failures = {
        "missing_page_metadata": len(
            missing_page_metadata
        ),
        "missing_structural_metadata": len(
            missing_structural_metadata
        ),
        "empty_chunks": len(
            empty_chunks
        ),
        "over_token_limit": len(
            over_limit
        ),
        "duplicate_chunk_ids": int(
            duplicate_chunk_ids
        ),
        "non_contiguous_indices": int(
            not contiguous_indices
        ),
    }

    status = (
        "PASS"
        if all(
            count == 0
            for count in hard_failures.values()
        )
        else "FAIL"
    )

    # ========================================================
    # 8. Save outputs
    # ========================================================

    write_documents_jsonl(
        FINAL_CHUNKS_PATH,
        final_chunks,
    )

    write_documents_jsonl(
        REJECTED_CHUNKS_PATH,
        rejected_chunks,
    )

    write_documents_jsonl(
        FIGURE_CAPTIONS_PATH,
        figure_documents,
    )

    write_documents_jsonl(
        TABLES_PATH,
        table_documents,
    )

    report = {
        "status": status,
        "parser": "pymupdf_layout",
        "parsed_document_types": (
            type_summary
        ),
        "body_documents": len(
            body_documents
        ),
        "figure_documents": len(
            figure_documents
        ),
        "table_documents": len(
            table_documents
        ),
        "cleaned_documents": len(
            cleaned_documents
        ),
        "structural_documents": len(
            structural_documents
        ),
        "candidate_chunks": len(
            candidate_chunks
        ),
        "accepted_chunks": len(
            final_chunks
        ),
        "rejected_chunks": len(
            rejected_chunks
        ),
        "rejection_counts": (
            validation_report.get(
                "rejection_counts",
                {},
            )
        ),
        "hard_failures": (
            hard_failures
        ),
    }

    if token_counts:
        report["token_statistics"] = {
            "minimum": min(
                token_counts
            ),
            "maximum": max(
                token_counts
            ),
            "average": mean(
                token_counts
            ),
            "median": median(
                token_counts
            ),
        }

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ========================================================
    # 9. Console summary
    # ========================================================

    print(
        "\nLAYOUT-AWARE CHUNKING PIPELINE"
    )
    print("=" * 80)

    print(
        f"Parsed layout Documents: "
        f"{len(parsed_documents)}"
    )

    print(
        f"Document type summary: "
        f"{type_summary}"
    )

    print(
        f"Body Documents: "
        f"{len(body_documents)}"
    )

    print(
        f"Figure Documents: "
        f"{len(figure_documents)}"
    )

    print(
        f"Table Documents: "
        f"{len(table_documents)}"
    )

    print(
        f"Cleaned Documents: "
        f"{len(cleaned_documents)}"
    )

    print(
        f"Structural Documents: "
        f"{len(structural_documents)}"
    )

    print(
        f"Candidate chunks: "
        f"{len(candidate_chunks)}"
    )

    print("\nQUALITY GATE")
    print("-" * 80)

    print(
        f"Accepted chunks: "
        f"{len(final_chunks)}"
    )

    print(
        f"Rejected chunks: "
        f"{len(rejected_chunks)}"
    )

    print(
        f"Rejection counts: "
        f"{validation_report.get('rejection_counts', {})}"
    )

    print("\nFINAL VALIDATION")
    print("-" * 80)

    for name, count in (
        hard_failures.items()
    ):
        print(
            f"{name}: {count}"
        )

    if page_numbers:
        print(
            f"Page range: "
            f"{min(page_numbers)}-"
            f"{max(page_numbers)}"
        )

    if token_counts:
        print("\nTOKEN STATISTICS")
        print("-" * 80)

        print(
            f"Minimum tokens: "
            f"{min(token_counts)}"
        )

        print(
            f"Maximum tokens: "
            f"{max(token_counts)}"
        )

        print(
            f"Average tokens: "
            f"{mean(token_counts):.2f}"
        )

        print(
            f"Median tokens: "
            f"{median(token_counts):.2f}"
        )

    print("\nSTATUS")
    print("-" * 80)

    print(status)

    print("=" * 80)

    print(
        f"Final corpus: "
        f"{FINAL_CHUNKS_PATH}"
    )

    print(
        f"Rejected chunks: "
        f"{REJECTED_CHUNKS_PATH}"
    )

    print(
        f"Figure captions: "
        f"{FIGURE_CAPTIONS_PATH}"
    )

    print(
        f"Tables: "
        f"{TABLES_PATH}"
    )

    print(
        f"Final report: "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    main()
