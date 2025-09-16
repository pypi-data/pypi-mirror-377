"""
Gemini Parallel: A utility package for parallel Gemini API calls with MongoDB logging.
"""

from .executor import ParallelExecutor
from .processors import ContentBuilder
from .mongo_logger import MongoLogger

__version__ = "0.1.0"
__all__ = ["ParallelExecutor", "ContentBuilder", "MongoLogger"]