import time

from src.config import BATCH_SIZE
from src.embedder import Embedder
from src.reader import ChunkReader
from src.writer import EmbeddingWriter


class EmbeddingPipeline:

    def __init__(
        self,
        input_file,
        output_file,
    ):

        self.reader = ChunkReader(
            input_file
        )

        self.embedder = Embedder()

        self.writer = EmbeddingWriter(
            output_file
        )

    def run(self):

        total_chunks = 0

        total_time = 0

        batch_number = 1

        print("\nStarting Embedding Pipeline\n")

        for batch in self.reader.batch_generator(
            BATCH_SIZE
        ):

            print("=" * 70)

            print(
                f"Batch : {batch_number}"
            )

            print(
                f"Chunks: {len(batch)}"
            )

            start = time.time()

            embeddings = self.embedder.embed_chunks(
                batch
            )

            elapsed = time.time() - start

            self.writer.append(
                batch,
                embeddings,
            )

            print(
                f"Time  : {elapsed:.2f} sec"
            )

            total_chunks += len(batch)

            total_time += elapsed

            batch_number += 1

        print("\n" + "=" * 70)

        print("Embedding Finished")

        print(
            f"Total Chunks : {total_chunks}"
        )

        print(
            f"Total Time   : {total_time:.2f} sec"
        )

        print(
            f"Average Speed: {total_chunks/total_time:.2f} chunks/sec"
        )





#### code to benchmark the embedding chunk size in pipeline
# import time

# from src.config import BATCH_SIZE
# from src.embedder import Embedder
# from src.reader import ChunkReader
# from src.writer import EmbeddingWriter


# class EmbeddingPipeline:

#     def __init__(
#         self,
#         input_file,
#         output_file,
#     ):

#         self.reader = ChunkReader(
#             input_file
#         )

#         self.embedder = Embedder()

#         self.writer = EmbeddingWriter(
#             output_file
#         )

#     def run(self):

#         print("\n" + "=" * 70)
#         print("Embedding Pipeline Benchmark")
#         print("=" * 70)

#         print(f"Batch Size : {BATCH_SIZE}")

#         batch_number = 1

#         for batch in self.reader.batch_generator(
#             BATCH_SIZE
#         ):

#             print("\n" + "=" * 70)
#             print(f"Benchmarking Batch {batch_number}")
#             print(f"Chunks : {len(batch)}")

#             start = time.perf_counter()

#             embeddings = self.embedder.embed_chunks(
#                 batch
#             )

#             embed_time = time.perf_counter() - start

#             self.writer.append(
#                 batch,
#                 embeddings,
#             )

#             print(f"\nEmbedding Time : {embed_time:.2f} sec")
#             print(f"Chunks/sec     : {len(batch) / embed_time:.2f}")

#             print("\nBenchmark complete.")
#             print("Stopping after first batch.\n")

#             # Stop after the first batch for benchmarking
#             break