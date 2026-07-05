from pathlib import Path
import hashlib
import json


CHUNKS_PATH = Path("output/chunks_v2.jsonl")
REPORT_PATH = Path("output/chunk_acceptance_report.json")

FINAL_PATH = Path("output/chunks_final.jsonl")
SUMMARY_PATH = Path("output/final_chunk_summary.json")


def load_jsonl(path: Path) -> list[dict]:
    items = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                items.append(json.loads(line))

    return items


def make_chunk_id(
    chunk_index: int,
    text: str,
) -> str:
    digest = hashlib.sha1(
        text.encode("utf-8")
    ).hexdigest()[:12]

    return (
        f"ckm-guideline:"
        f"{chunk_index:05d}:"
        f"{digest}"
    )


def main():
    chunks = load_jsonl(CHUNKS_PATH)

    with REPORT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    # Fixed decision rule:
    # remove only chunks explicitly identified
    # as running page furniture.
    rejected_indices = set(
        report["failures"]["running_furniture"]
    )

    final_chunks = [
        chunk
        for chunk in chunks
        if chunk["chunk_index"] not in rejected_indices
    ]

    # Rebuild contiguous indices and stable IDs.
    for new_index, chunk in enumerate(final_chunks):
        chunk["chunk_index"] = new_index

        chunk["chunk_id"] = make_chunk_id(
            new_index,
            chunk["text"],
        )

    with FINAL_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        for chunk in final_chunks:
            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    word_counts = [
        chunk["word_count"]
        for chunk in final_chunks
    ]

    summary = {
        "input_chunks": len(chunks),
        "removed_running_furniture_chunks": len(
            rejected_indices
        ),
        "removed_original_indices": sorted(
            rejected_indices
        ),
        "final_chunks": len(final_chunks),
        "min_words": min(word_counts),
        "max_words": max(word_counts),
        "average_words": round(
            sum(word_counts) / len(word_counts),
            2,
        ),
        "pages_min": min(
            chunk["page_start"]
            for chunk in final_chunks
        ),
        "pages_max": max(
            chunk["page_end"]
            for chunk in final_chunks
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

    print("FINAL CHUNK CORPUS CREATED")
    print("=" * 80)
    print(
        f"Input chunks: "
        f"{summary['input_chunks']}"
    )
    print(
        f"Removed furniture chunks: "
        f"{summary['removed_running_furniture_chunks']}"
    )
    print(
        f"Final chunks: "
        f"{summary['final_chunks']}"
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
        f"Page range: "
        f"{summary['pages_min']}-"
        f"{summary['pages_max']}"
    )

    print(f"\nSaved final corpus: {FINAL_PATH}")
    print(f"Saved summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()

    