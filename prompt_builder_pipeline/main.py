from pathlib import Path

from src.pipeline import PromptPipeline


INPUT_FILE = Path("input") / "reranked_results.json"
OUTPUT_FILE = Path("output") / "final_prompt.txt"


def main():
    question = input("Enter your question: ").strip()

    pipeline = PromptPipeline(str(INPUT_FILE))
    response = pipeline.run(question)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(response.prompt)

    print("=" * 60)
    print("Prompt Builder Pipeline Completed")
    print("=" * 60)
    print(f"Token Count : {response.token_count}")
    print(f"Output File : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()