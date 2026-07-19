from src.config import (
    SYSTEM_PROMPT,
    MAX_CONTEXT_TOKENS,
)
from src.models import (
    PromptContext,
    PromptRequest,
)
from src.reader import PromptReader
from src.truncator import Truncator
from src.prompt_builder import PromptBuilder


class PromptPipeline:
    def __init__(self, input_file: str):
        self.reader = PromptReader(input_file)
        self.truncator = Truncator(MAX_CONTEXT_TOKENS)
        self.prompt_builder = PromptBuilder()

    def run(self, question: str):
        # Read reranked chunks
        chunks = self.reader.read()

        # Truncate context
        selected_chunks = self.truncator.truncate(chunks)

        # Build prompt context
        context = PromptContext(
            question=question,
            chunks=selected_chunks
        )

        # Create request
        request = PromptRequest(
            system_prompt=SYSTEM_PROMPT,
            context=context
        )

        # Build final prompt
        response = self.prompt_builder.build(request)

        return response