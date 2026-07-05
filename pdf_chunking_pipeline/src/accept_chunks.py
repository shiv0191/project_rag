from pathlib import Path
import json
import re
import sys


INPUT_PATH = Path("output/chunks_v2.jsonl")
REPORT_PATH = Path("output/chunk_acceptance_report.json")

MAX_WORDS = 450


def load_chunks() -> list[dict]:
    chunks = []

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                chunks.append(json.loads(line))

    return chunks


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_heading_only(text: str) -> bool:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return True

    return all(
        re.match(r"^#{1,6}\s+\S+", line)
        for line in lines
    )


def contains_running_furniture(text: str) -> bool:
    compact = normalized_text(text)

    patterns = [
        r"J\s+A\s+C\s+C\s+V\s+O\s+L\s*\.",
        r"J\s+U\s+N\s+E\s+9\s*,\s*2\s+0\s+2\s+6",
        r"Ndumele et al.*CKM Guideline",
    ]

    return any(
        re.search(
            pattern,
            compact,
            flags=re.IGNORECASE,
        )
        for pattern in patterns
    )


def looks_like_reference_interleaving(text: str) -> bool:
    """
    Detect strong evidence of bibliography-like numeric
    interleaving inside the primary 1-83 corpus.

    This is intentionally conservative.
    """
    numbers = []

    for line in text.splitlines():
        match = re.match(
            r"^\s*(\d{1,3})\.\s+",
            line,
        )

        if match:
            numbers.append(int(match.group(1)))

    if len(numbers) < 4:
        return False

    decreases = sum(
        current < previous
        for previous, current in zip(
            numbers,
            numbers[1:],
        )
    )

    return decreases >= 2


def main():
    chunks = load_chunks()

    failures = {
        "empty_text": [],
        "over_max_words": [],
        "heading_only": [],
        "running_furniture": [],
        "invalid_pages": [],
        "reference_interleaving": [],
    }

    warnings = {
        "very_short_under_20_words": [],
        "short_under_60_words": [],
    }

    seen_ids = set()
    duplicate_ids = []

    for chunk in chunks:
        index = chunk["chunk_index"]
        text = chunk.get("text", "")
        words = chunk.get("word_count", 0)
        pages = chunk.get("page_numbers", [])
        chunk_id = chunk.get("chunk_id", "")

        if not text.strip():
            failures["empty_text"].append(index)

        if words > MAX_WORDS:
            failures["over_max_words"].append(index)

        if is_heading_only(text):
            failures["heading_only"].append(index)

        if contains_running_furniture(text):
            failures["running_furniture"].append(index)

        if (
            not pages
            or min(pages) < 1
            or max(pages) > 83
        ):
            failures["invalid_pages"].append(index)

        if looks_like_reference_interleaving(text):
            failures["reference_interleaving"].append(index)

        if words < 20:
            warnings[
                "very_short_under_20_words"
            ].append(index)

        if words < 60:
            warnings[
                "short_under_60_words"
            ].append(index)

        if chunk_id in seen_ids:
            duplicate_ids.append(chunk_id)

        seen_ids.add(chunk_id)

    # Structural invariants
    expected_indices = list(range(len(chunks)))
    actual_indices = [
        chunk["chunk_index"]
        for chunk in chunks
    ]

    contiguous_indices = (
        actual_indices == expected_indices
    )

    unique_chunk_ids = (
        len(duplicate_ids) == 0
    )

    failure_count = sum(
        len(items)
        for items in failures.values()
    )

    hard_pass = (
        len(chunks) > 0
        and contiguous_indices
        and unique_chunk_ids
        and failure_count == 0
    )

    report = {
        "status": "PASS" if hard_pass else "FAIL",
        "total_chunks": len(chunks),
        "contiguous_indices": contiguous_indices,
        "unique_chunk_ids": unique_chunk_ids,
        "duplicate_ids": duplicate_ids,
        "failure_count": failure_count,
        "failures": failures,
        "warnings": warnings,
    }

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("CHUNK ACCEPTANCE GATE")
    print("=" * 80)
    print(f"Status: {report['status']}")
    print(f"Total chunks: {len(chunks)}")
    print(
        f"Contiguous indices: "
        f"{contiguous_indices}"
    )
    print(
        f"Unique chunk IDs: "
        f"{unique_chunk_ids}"
    )
    print(
        f"Hard failures: "
        f"{failure_count}"
    )

    print("\nFAILURE COUNTS")
    print("-" * 80)

    for name, indices in failures.items():
        print(
            f"{name}: {len(indices)}"
        )

    print("\nWARNING COUNTS")
    print("-" * 80)

    for name, indices in warnings.items():
        print(
            f"{name}: {len(indices)}"
        )

    print(
        f"\nSaved report: {REPORT_PATH}"
    )

    # Useful for CI / automation:
    # PASS -> exit code 0
    # FAIL -> exit code 1
    sys.exit(0 if hard_pass else 1)


if __name__ == "__main__":
    main()

