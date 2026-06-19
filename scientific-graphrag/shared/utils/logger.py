"""
Shared utilities for the platform
"""

import logging
from typing import Any, Dict
from datetime import datetime


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup logging for a module"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


class GraphRAGException(Exception):
    """Base exception for GraphRAG platform"""
    pass


class RetrievalException(GraphRAGException):
    """Exception during retrieval"""
    pass


class GraphException(GraphRAGException):
    """Exception during graph operations"""
    pass


class EmbeddingException(GraphRAGException):
    """Exception during embedding"""
    pass


class AgentException(GraphRAGException):
    """Exception during agent execution"""
    pass


def format_duration(milliseconds: float) -> str:
    """Format duration in milliseconds to readable string"""
    if milliseconds < 1000:
        return f"{milliseconds:.0f}ms"
    else:
        seconds = milliseconds / 1000
        return f"{seconds:.2f}s"


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
