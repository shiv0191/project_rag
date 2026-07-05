import tiktoken

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


TOKENIZER_NAME = "cl100k_base"

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 75


def build_token_length_function():
    """
    Build a deterministic token-counting function.

    cl100k_base is used only for chunk-size measurement.
    It does not couple the pipeline to an embedding model.
    """

    encoding = tiktoken.get_encoding(
        TOKENIZER_NAME
    )

    def token_length(text: str) -> int:
        return len(
            encoding.encode(
                text,
                disallowed_special=(),
            )
        )

    return token_length


def build_recursive_splitter():
    """
    Create a LangChain recursive splitter using
    token-based length measurement.

    Important:
    - recursive boundary selection
    - token-aware size control
    - controlled overlap
    - metadata preserved by split_documents()
    """

    token_length = build_token_length_function()

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE_TOKENS,
        chunk_overlap=CHUNK_OVERLAP_TOKENS,
        length_function=token_length,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        keep_separator=True,
        strip_whitespace=True,
    )


def split_structural_documents(
    structural_documents: list[Document],
) -> list[Document]:
    """
    Split structural Documents into retrieval-sized
    child chunks.

    LangChain preserves parent metadata on child chunks.
    """

    if not structural_documents:
        return []

    splitter = build_recursive_splitter()

    chunks = splitter.split_documents(
        structural_documents
    )

    token_length = build_token_length_function()

    results = []

    for chunk_index, chunk in enumerate(chunks):
        text = chunk.page_content.strip()

        if not text:
            continue

        metadata = dict(chunk.metadata)

        metadata.update(
            {
                "chunk_index": chunk_index,
                "content_type": "retrieval_chunk",
                "token_count": token_length(text),
                "chunk_size_tokens": CHUNK_SIZE_TOKENS,
                "chunk_overlap_tokens": CHUNK_OVERLAP_TOKENS,
                "tokenizer": TOKENIZER_NAME,
            }
        )

        results.append(
            Document(
                page_content=text,
                metadata=metadata,
            )
        )

    return results

