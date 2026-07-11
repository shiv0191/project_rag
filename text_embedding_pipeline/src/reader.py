import json


class ChunkReader:

    def __init__(self, input_file):
        self.input_file = input_file

    def batch_generator(self, batch_size):

        batch = []

        with open(
            self.input_file,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                document = json.loads(line)

                chunk = {
                    "chunk_id": document["metadata"]["chunk_id"],
                    "page": document["metadata"]["page_number"],
                    "text": document["page_content"],
                    "metadata": document["metadata"],
                }

                batch.append(chunk)

                if len(batch) == batch_size:
                    yield batch
                    batch = []

        if batch:
            yield batch
