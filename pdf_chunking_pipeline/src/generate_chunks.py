from pathlib import Path
import hashlib
import json
import re


INPUT_PATH = Path("output/parsed_pages.json")
OUTPUT_PATH = Path("output/chunks_v2.jsonl")
REJECTED_PATH = Path("output/rejected_blocks.jsonl")
SUMMARY_PATH = Path("output/chunk_summary_v2.json")


TARGET_WORDS = 320
MAX_WORDS = 450
MIN_WORDS = 60


# Based on the actual audit:
# page 84 begins the references region and extraction becomes
# column-interleaved. Keep it outside the primary v1 semantic index.
PRIMARY_CONTENT_LAST_PAGE = 83


def word_count(text: str) -> int:
    return len(text.split())


def clean_page_furniture(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    cleaned_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            cleaned_lines.append("")
            continue

        # JACC running publication header/footer.
        if re.search(
            r"J\s+A\s+C\s+C\s+V\s+O\s+L\s*\.",
            line,
            flags=re.IGNORECASE,
        ):
            continue

        if re.search(
            r"J\s+U\s+N\s+E\s+9\s*,\s*2\s+0\s+2\s+6",
            line,
            flags=re.IGNORECASE,
        ):
            continue

        # Page furniture such as:
        # > e1900 Ndumele et al 2026 AHA/... Guideline
        # Ndumele et al e1989 2026 AHA/... Guideline
        compact = re.sub(r"\s+", " ", line)

        if (
            "Ndumele et al" in compact
            and "CKM Guideline" in compact
        ):
            continue

        # Standalone article page identifiers.
        if re.fullmatch(r">?\s*e\d{4}\s*", compact):
            continue

        # Standalone author running header.
        if re.fullmatch(
            r">?\s*Ndumele et al\s*",
            compact,
            flags=re.IGNORECASE,
        ):
            continue

        # First-page publisher boilerplate.
        if re.search(
            r"AMERICAN HEART ASSOCIATION.*"
            r"AMERICAN COLLEGE OF CARDIOLOGY FOUNDATION",
            compact,
            flags=re.IGNORECASE,
        ):
            continue

        if re.search(
            r"PUBLISHED BY ELSEVIER",
            compact,
            flags=re.IGNORECASE,
        ):
            continue

        cleaned_lines.append(raw_line.rstrip())

    text = "\n".join(cleaned_lines)

    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_blocks(text: str) -> list[str]:
    return [
        block.strip()
        for block in re.split(r"\n\s*\n", text)
        if block.strip()
    ]


def heading_info(block: str):
    """
    Return (level, text) for a Markdown heading.
    Otherwise return None.
    """
    first_line = block.splitlines()[0].strip()

    match = re.match(
        r"^(#{1,6})\s+(.+)$",
        first_line,
    )

    if not match:
        return None

    level = len(match.group(1))
    text = match.group(2).strip()

    return level, text


def update_heading_path(
    heading_path: list[str],
    level: int,
    text: str,
) -> list[str]:
    """
    Maintain H1/H2/H3/... hierarchy.
    """
    new_path = list(heading_path)

    while len(new_path) >= level:
        new_path.pop()

    while len(new_path) < level - 1:
        new_path.append("")

    new_path.append(text)

    return [
        item
        for item in new_path
        if item
    ]


def looks_like_markdown_table(block: str) -> bool:
    lines = [
        line.strip()
        for line in block.splitlines()
        if line.strip()
    ]

    pipe_lines = sum(
        line.count("|") >= 2
        for line in lines
    )

    return pipe_lines >= 2


def table_is_malformed(block: str) -> bool:
    """
    Conservative detector.

    Reject only tables showing strong evidence of extraction damage.
    """
    if not looks_like_markdown_table(block):
        return False

    lines = [
        line.strip()
        for line in block.splitlines()
        if line.strip()
    ]

    # Strong corruption signals seen in the actual audit:
    # fragmented words and prose mixed across many columns.
    suspicious_fragments = [
        r"\|\s*Man\|agement of\|",
        r"\|\*\*Recomm\*\*",
        r"\|\s*2Idltith",
        r"Inadultswith",
        r"syndromestae",
        r"\|prevent\s*$",
    ]

    for pattern in suspicious_fragments:
        if re.search(
            pattern,
            block,
            flags=re.IGNORECASE | re.MULTILINE,
        ):
            return True

    # Very wide tables with many rows are high risk when
    # extracted from multi-column clinical layouts.
    column_counts = [
        max(0, line.count("|") - 1)
        for line in lines
        if "|" in line
    ]

    if column_counts:
        max_columns = max(column_counts)

        if max_columns >= 5 and len(lines) >= 8:
            return True

    return False


def split_oversized_text(
    text: str,
    max_words: int = MAX_WORDS,
) -> list[str]:
    if word_count(text) <= max_words:
        return [text]

    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9(\[])",
        text,
    )

    pieces = []
    current = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if word_count(sentence) > max_words:
            if current:
                pieces.append(
                    " ".join(current).strip()
                )
                current = []

            words = sentence.split()

            for start in range(
                0,
                len(words),
                max_words,
            ):
                piece = " ".join(
                    words[start:start + max_words]
                ).strip()

                if piece:
                    pieces.append(piece)

            continue

        candidate = " ".join(
            current + [sentence]
        ).strip()

        if (
            current
            and word_count(candidate) > max_words
        ):
            pieces.append(
                " ".join(current).strip()
            )
            current = [sentence]
        else:
            current.append(sentence)

    if current:
        pieces.append(
            " ".join(current).strip()
        )

    return pieces


def make_chunk_id(
    chunk_index: int,
    text: str,
) -> str:
    digest = hashlib.sha1(
        text.encode("utf-8")
    ).hexdigest()[:12]

    return f"ckm-guideline:{chunk_index:05d}:{digest}"


def flush_chunk(
    chunks: list[dict],
    current_items: list[dict],
    section_path: list[str],
):
    if not current_items:
        return

    text = "\n\n".join(
        item["text"]
        for item in current_items
    ).strip()

    if not text:
        return

    pages = sorted(
        {
            page
            for item in current_items
            for page in item["page_numbers"]
        }
    )

    chunks.append(
        {
            "chunk_id": "",
            "chunk_index": 0,
            "text": text,
            "word_count": word_count(text),
            "page_numbers": pages,
            "page_start": min(pages),
            "page_end": max(pages),
            "section_path": list(section_path),
            "source": "ckm_guideline_2026",
        }
    )


def main():
    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        pages = json.load(file)

    logical_items = []
    rejected = []

    heading_path = []

    for page in pages:
        page_number = page["pdf_page_number"]

        # Fixed corpus boundary for v1.
        if page_number > PRIMARY_CONTENT_LAST_PAGE:
            rejected.append(
                {
                    "page_number": page_number,
                    "reason": "outside_primary_clinical_corpus",
                    "text_preview": (
                        page.get("text", "")[:300]
                    ),
                }
            )
            continue

        text = clean_page_furniture(
            page.get("text", "")
        )

        if not text:
            continue

        blocks = split_into_blocks(text)

        for block in blocks:
            info = heading_info(block)

            if info:
                level, title = info

                heading_path = update_heading_path(
                    heading_path,
                    level,
                    title,
                )

                # Heading is stored as pending context.
                # It is NOT emitted as a standalone chunk.
                logical_items.append(
                    {
                        "kind": "heading",
                        "text": block,
                        "page_numbers": [page_number],
                        "section_path": list(
                            heading_path
                        ),
                    }
                )
                continue

            if table_is_malformed(block):
                rejected.append(
                    {
                        "page_number": page_number,
                        "reason": "malformed_table",
                        "text_preview": block[:500],
                    }
                )
                continue

            logical_items.append(
                {
                    "kind": "content",
                    "text": block,
                    "page_numbers": [page_number],
                    "section_path": list(
                        heading_path
                    ),
                }
            )

    chunks = []
    current_items = []
    current_section_path = []
    pending_headings = []

    for item in logical_items:
        if item["kind"] == "heading":
            # Flush previous semantic region.
            if current_items:
                flush_chunk(
                    chunks,
                    current_items,
                    current_section_path,
                )
                current_items = []

            pending_headings.append(item)
            current_section_path = item[
                "section_path"
            ]
            continue

        # Content item.
        pieces = split_oversized_text(
            item["text"]
        )

        for piece_index, piece in enumerate(pieces):
            piece_item = {
                "text": piece,
                "page_numbers": item[
                    "page_numbers"
                ],
            }

            # Attach pending headings only when actual
            # content arrives.
            if pending_headings:
                heading_text = "\n\n".join(
                    heading["text"]
                    for heading in pending_headings
                )

                heading_pages = sorted(
                    {
                        page
                        for heading in pending_headings
                        for page in heading[
                            "page_numbers"
                        ]
                    }
                )

                heading_item = {
                    "text": heading_text,
                    "page_numbers": heading_pages,
                }

                current_items.append(
                    heading_item
                )

                pending_headings = []

            candidate_items = (
                current_items + [piece_item]
            )

            candidate_text = "\n\n".join(
                candidate["text"]
                for candidate in candidate_items
            )

            if (
                current_items
                and word_count(candidate_text)
                > TARGET_WORDS
            ):
                flush_chunk(
                    chunks,
                    current_items,
                    current_section_path,
                )
                current_items = []

            current_items.append(piece_item)

            current_text = "\n\n".join(
                current["text"]
                for current in current_items
            )

            if word_count(current_text) >= MAX_WORDS:
                flush_chunk(
                    chunks,
                    current_items,
                    current_section_path,
                )
                current_items = []

    flush_chunk(
        chunks,
        current_items,
        current_section_path,
    )

    # Merge tiny chunks only when section context matches.
    merged = []
    index = 0

    while index < len(chunks):
        chunk = chunks[index]

        if (
            chunk["word_count"] < MIN_WORDS
            and index + 1 < len(chunks)
        ):
            next_chunk = chunks[index + 1]

            same_section = (
                chunk["section_path"]
                == next_chunk["section_path"]
            )

            combined_text = (
                chunk["text"]
                + "\n\n"
                + next_chunk["text"]
            ).strip()

            if (
                same_section
                and word_count(combined_text)
                <= MAX_WORDS
            ):
                pages = sorted(
                    set(
                        chunk["page_numbers"]
                        + next_chunk["page_numbers"]
                    )
                )

                merged.append(
                    {
                        "chunk_id": "",
                        "chunk_index": 0,
                        "text": combined_text,
                        "word_count": word_count(
                            combined_text
                        ),
                        "page_numbers": pages,
                        "page_start": min(pages),
                        "page_end": max(pages),
                        "section_path": chunk[
                            "section_path"
                        ],
                        "source": (
                            "ckm_guideline_2026"
                        ),
                    }
                )

                index += 2
                continue

        merged.append(chunk)
        index += 1

    # Stable final IDs.
    for index, chunk in enumerate(merged):
        chunk["chunk_index"] = index
        chunk["chunk_id"] = make_chunk_id(
            index,
            chunk["text"],
        )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        for chunk in merged:
            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    with REJECTED_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        for item in rejected:
            file.write(
                json.dumps(
                    item,
                    ensure_ascii=False,
                )
                + "\n"
            )

    counts = [
        chunk["word_count"]
        for chunk in merged
    ]

    summary = {
        "total_chunks": len(merged),
        "min_words": min(counts),
        "max_words": max(counts),
        "average_words": round(
            sum(counts) / len(counts),
            2,
        ),
        "chunks_under_min": sum(
            count < MIN_WORDS
            for count in counts
        ),
        "chunks_over_max": sum(
            count > MAX_WORDS
            for count in counts
        ),
        "rejected_items": len(rejected),
        "primary_content_pages": (
            PRIMARY_CONTENT_LAST_PAGE
        ),
    }

    with SUMMARY_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("CHUNK GENERATION V2 COMPLETE")
    print("=" * 80)
    print(
        f"Primary content pages: "
        f"1-{PRIMARY_CONTENT_LAST_PAGE}"
    )
    print(
        f"Total chunks: "
        f"{summary['total_chunks']}"
    )
    print(
        f"Minimum words: "
        f"{summary['min_words']}"
    )
    print(
        f"Maximum words: "
        f"{summary['max_words']}"
    )
    print(
        f"Average words: "
        f"{summary['average_words']}"
    )
    print(
        f"Chunks under {MIN_WORDS} words: "
        f"{summary['chunks_under_min']}"
    )
    print(
        f"Chunks over {MAX_WORDS} words: "
        f"{summary['chunks_over_max']}"
    )
    print(
        f"Rejected items: "
        f"{summary['rejected_items']}"
    )
    print(f"\nSaved chunks: {OUTPUT_PATH}")
    print(f"Saved rejected: {REJECTED_PATH}")
    print(f"Saved summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()

