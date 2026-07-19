from src.config import (
    PROMPT_TEMPLATE,
)
from src.models import (
    PromptRequest,
    PromptResponse,
)
from src.formatter import Formatter
from src.citation_builder import CitationBuilder
from src.tokenizer import Tokenizer


class PromptBuilder:
    def __init__(self):
        self.formatter = Formatter()
        self.citation_builder = CitationBuilder()
        self.tokenizer = Tokenizer()

    def build(self, request: PromptRequest) -> PromptResponse:
        """
        Build the final prompt.
        """

        context = self.formatter.format_context(
            request.context.chunks
        )

        citations = self.citation_builder.build(
            request.context.chunks
        )

        if citations:
            context += "\n\nSources:\n"
            context += citations

        prompt = PROMPT_TEMPLATE.format(
            system_prompt=request.system_prompt,
            context=context,
            question=request.context.question
        )

        token_count = self.tokenizer.count_prompt_tokens(prompt)

        return PromptResponse(
            prompt=prompt,
            token_count=token_count
        )