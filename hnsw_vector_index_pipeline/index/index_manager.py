import json
from pathlib import Path


class IndexManager:

    @staticmethod
    def save(index, index_file: Path):

        index.save_index(str(index_file))

    @staticmethod
    def load(index, index_file: Path):

        index.load_index(str(index_file))

        return index

    @staticmethod
    def save_mapping(mapping: dict, mapping_file: Path):

        with open(mapping_file, "w", encoding="utf-8") as file:

            json.dump(mapping, file, indent=4)

    @staticmethod
    def load_mapping(mapping_file: Path):

        with open(mapping_file, "r", encoding="utf-8") as file:

            return json.load(file)