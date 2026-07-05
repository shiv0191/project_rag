from pathlib import Path
import json

import pymupdf4llm


PDF_PATH = Path(
    "data/ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf"
)

OUTPUT_DIR = Path("output")
OUTPUT_PATH = OUTPUT_DIR / "parsed_pages.json"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Parsing PDF: {PDF_PATH}")

    pages = pymupdf4llm.to_markdown(
        str(PDF_PATH),
        page_chunks=True,
        show_progress=True,
    )

    print(f"\nParsed pages: {len(pages)}")

    serializable_pages = []

    for index, page in enumerate(pages):
        text = page.get("text", "")

        serializable_pages.append(
            {
                "pdf_page_index": index,
                "pdf_page_number": index + 1,
                "text": text,
                "text_length": len(text),
                "metadata": page.get("metadata", {}),
            }
        )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            serializable_pages,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    print(f"Saved parsed output to: {OUTPUT_PATH}")

    print("\nPAGE LENGTH SUMMARY")
    print("=" * 80)

    for page in serializable_pages:
        print(
            f"Page {page['pdf_page_number']:03d} | "
            f"characters={page['text_length']}"
        )


if __name__ == "__main__":
    main()
    