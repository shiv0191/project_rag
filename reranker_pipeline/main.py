from src.pipeline import RerankerPipeline


def main():
    pipeline = RerankerPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()