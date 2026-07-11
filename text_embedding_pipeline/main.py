from src.pipeline import EmbeddingPipeline


def main():

    pipeline = EmbeddingPipeline(

        input_file="input/chunks_final.jsonl",

        output_file="output/embeddings.jsonl",

    )

    pipeline.run()


if __name__ == "__main__":
    main()
