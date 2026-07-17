import json

# from src.config import PAYLOADS_FILE
from src.config import EMBEDDINGS_FILE


class PayloadLoader:
    def __init__(self):
        self.payloads = {}

    def load(self):
        """
        Load payloads.jsonl into memory.

        Returns:
            dict[str, dict]
        """

        # with open(PAYLOADS_FILE, "r", encoding="utf-8") as file:
        with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                payload = json.loads(line)

                self.payloads[payload["chunk_id"]] = payload

        print(f"Loaded {len(self.payloads)} payloads")

        return self.payloads

    def get(self, chunk_id: str):
        """
        Retrieve payload by chunk id.
        """
        return self.payloads.get(chunk_id)
