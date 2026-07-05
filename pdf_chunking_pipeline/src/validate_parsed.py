from pathlib import Path
import json
import re
import statistics


INPUT_PATH = Path("output/parsed_pages.json")
REPORT_PATH = Path("output/validation_report.json")


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def main():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        pages = json.load(file)

    lengths = [page["text_length"] for page in pages]

    median_length = statistics.median(lengths)

    empty_pages = []
    short_pages = []
    long_pages = []

    line_occurrences = {}

    for page in pages:
        page_number = page["pdf_page_number"]
        text = page.get("text", "")

        if not text.strip():
            empty_pages.append(page_number)

        if len(text) < 500:
            short_pages.append(
                {
                    "page": page_number,
                    "characters": len(text),
                }
            )

        if len(text) > median_length * 1.75:
            long_pages.append(
                {
                    "page": page_number,
                    "characters": len(text),
                }
            )

        # Track repeated lines across pages.
        # Useful for finding recurring headers and footers.
        unique_lines_on_page = set()

        for raw_line in text.splitlines():
            line = normalize_line(raw_line)

            # Ignore tiny fragments.
            if len(line) < 12:
                continue

            unique_lines_on_page.add(line)

        for line in unique_lines_on_page:
            line_occurrences.setdefault(line, []).append(page_number)

    repeated_lines = []

    for line, page_numbers in line_occurrences.items():
        if len(page_numbers) >= 5:
            repeated_lines.append(
                {
                    "text": line,
                    "page_count": len(page_numbers),
                    "pages": page_numbers,
                }
            )

    repeated_lines.sort(
        key=lambda item: item["page_count"],
        reverse=True,
    )

    report = {
        "total_pages": len(pages),
        "median_page_characters": median_length,
        "empty_pages": empty_pages,
        "short_pages": short_pages,
        "long_pages": long_pages,
        "top_repeated_lines": repeated_lines[:30],
    }

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total pages: {len(pages)}")
    print(f"Median page characters: {median_length}")
    print(f"Empty pages: {empty_pages}")

    print("\nSHORT PAGES (< 500 characters)")
    print("-" * 80)

    if short_pages:
        for item in short_pages:
            print(
                f"Page {item['page']:03d} | "
                f"characters={item['characters']}"
            )
    else:
        print("None")

    print("\nUNUSUALLY LONG PAGES (> 1.75 x median)")
    print("-" * 80)

    if long_pages:
        for item in long_pages:
            print(
                f"Page {item['page']:03d} | "
                f"characters={item['characters']}"
            )
    else:
        print("None")

    print("\nTOP REPEATED LINES")
    print("-" * 80)

    if repeated_lines:
        for item in repeated_lines[:15]:
            print(
                f"{item['page_count']:3d} pages | "
                f"{item['text'][:120]}"
            )
    else:
        print("None")

    print(f"\nSaved report to: {REPORT_PATH}")


if __name__ == "__main__":
    main()

