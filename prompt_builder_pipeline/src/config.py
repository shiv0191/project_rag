import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# LLM Configuration
# ==========================================================

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")

MAX_CONTEXT_TOKENS = int(
    os.getenv("MAX_CONTEXT_TOKENS", 6000)
)

MAX_GENERATION_TOKENS = int(
    os.getenv("MAX_GENERATION_TOKENS", 1000)
)

# ==========================================================
# Prompt Configuration
# ==========================================================

SYSTEM_PROMPT = """
You are an expert AI assistant.

Answer the user's question ONLY using the provided context.

If the answer cannot be found in the context,
reply with:

"I don't know based on the provided context."

Do not make up facts.
""".strip()

# ==========================================================
# Formatting
# ==========================================================

CONTEXT_SEPARATOR = "\n\n" + "=" * 80 + "\n\n"

CHUNK_SEPARATOR = "\n" + "-" * 60 + "\n"

PAGE_TEMPLATE = (
    "Source: {source}\n"
    "Page: {page}\n\n"
    "{text}"
)

# ==========================================================
# Output Template
# ==========================================================

PROMPT_TEMPLATE = """
{system_prompt}

Context:

{context}

Question:

{question}

Answer:
""".strip()