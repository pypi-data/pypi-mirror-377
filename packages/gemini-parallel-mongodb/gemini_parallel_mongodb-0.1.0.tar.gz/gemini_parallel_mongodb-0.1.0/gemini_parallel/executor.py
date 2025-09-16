"""
Parallel executor for Gemini API calls with MongoDB logging support.
"""

import asyncio
import time
import uuid
import os
from typing import List, Dict, Any, Optional, Union
from google import genai
from google.genai import types
from tqdm.asyncio import tqdm

from .mongo_logger import MongoLogger


class ParallelExecutor:
    """Parallel executor for Gemini API calls with optional MongoDB logging."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        max_concurrent: int = 50,
        request_delay: float = 0.02,
        max_retries: int = 3,
        mongodb_uri: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize parallel executor.

        Args:
            model: Gemini model to use
            max_concurrent: Maximum concurrent API requests
            request_delay: Delay between requests (seconds)
            max_retries: Maximum retry attempts
            mongodb_uri: MongoDB URI for logging (optional)
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.model = model
        self.max_concurrent = max_concurrent
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.session_id = str(uuid.uuid4())

        # Initialize Gemini client
        self.client = genai.Client(
            api_key=api_key or os.environ.get("GEMINI_API_KEY")
        )

        # Initialize MongoDB logger if URI provided
        self.mongo_logger = MongoLogger(mongodb_uri) if mongodb_uri else None

    async def _execute_single(
        self,
        content: Dict[str, Any],
        semaphore: asyncio.Semaphore,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Execute single API call with logging and retry logic.

        Args:
            content: Content dictionary with processed input
            semaphore: Concurrency control semaphore
            request_id: Unique request identifier

        Returns:
            Result dictionary with response or error
        """
        async with semaphore:
            start_time = time.time()

            # Rate limiting
            await asyncio.sleep(self.request_delay)

            # Retry loop
            for attempt in range(self.max_retries):
                try:
                    # Make API call
                    response = await self.client.aio.models.generate_content(
                        model=self.model,
                        contents=content["contents"],
                        config=content.get("config")
                    )

                    if not response.text:
                        if attempt == self.max_retries - 1:
                            raise Exception("Empty API response")
                        await asyncio.sleep(2 ** attempt)
                        continue

                    duration_ms = (time.time() - start_time) * 1000

                    # Log successful call
                    if self.mongo_logger:
                        await self.mongo_logger.log_call({
                            "session_id": self.session_id,
                            "request_id": request_id,
                            "status": "success",
                            "prompt": str(content["contents"]),
                            "response": response.text,
                            "duration_ms": duration_ms,
                            "model": self.model,
                            "mode": content.get("mode", "text"),
                            "tokens_input": getattr(response.usage_metadata, 'prompt_token_count', None),
                            "tokens_output": getattr(response.usage_metadata, 'candidates_token_count', None)
                        })

                    return {
                        "request_id": request_id,
                        "status": "success",
                        "response": response.text,
                        "duration_ms": duration_ms,
                        "usage": response.usage_metadata if hasattr(response, 'usage_metadata') else None
                    }

                except Exception as e:
                    if attempt == self.max_retries - 1:
                        duration_ms = (time.time() - start_time) * 1000

                        # Log failed call
                        if self.mongo_logger:
                            await self.mongo_logger.log_call({
                                "session_id": self.session_id,
                                "request_id": request_id,
                                "status": "failed",
                                "prompt": str(content["contents"]),
                                "error": str(e),
                                "duration_ms": duration_ms,
                                "model": self.model,
                                "mode": content.get("mode", "text")
                            })

                        return {
                            "request_id": request_id,
                            "status": "failed",
                            "error": str(e),
                            "duration_ms": duration_ms
                        }

                    await asyncio.sleep(2 ** attempt)

    async def run_parallel(
        self,
        items: List[Any],
        mode: str = "text",
        response_schema: Optional[Any] = None,
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run parallel API calls with MongoDB logging.

        Args:
            items: List of inputs (prompts, content objects, etc.)
            mode: Processing mode ("text", "multimodal", "structured")
            response_schema: Pydantic model or dict for structured output
            show_progress: Show progress bar

        Returns:
            List of result dictionaries
        """
        if not items:
            return []

        print(f"🚀 Starting parallel analysis of {len(items)} items")
        print(f"📊 Max concurrent requests: {self.max_concurrent}")
        print(f"⏱️ Request delay: {self.request_delay}s")
        print(f"🎯 Session ID: {self.session_id}")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Process items based on mode
        processed_items = []
        for i, item in enumerate(items):
            content = {"contents": item, "mode": mode}

            if mode == "structured" and response_schema:
                content["config"] = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1
                )

            processed_items.append(content)

        # Create tasks for all items
        tasks = [
            self._execute_single(content, semaphore, f"req_{i}")
            for i, content in enumerate(processed_items)
        ]

        start_time = time.time()

        # Execute all tasks in parallel with optional progress bar
        if show_progress:
            results = await tqdm.gather(
                *tasks,
                desc="🧠 Processing items",
                ncols=120,
                unit=" items",
                colour="green"
            )
        else:
            results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Calculate statistics
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful

        print("✅ Analysis completed!")
        print(f"📈 Total time: {total_time:.2f}s")
        print(f"📊 Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⚡ Average time per item: {total_time / len(items):.3f}s")
        print(f"🚀 Items per second: {len(items) / total_time:.2f}")

        return results

    async def get_session_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics for current session from MongoDB.

        Returns:
            Dictionary with session statistics or None if no logger
        """
        if not self.mongo_logger:
            return None

        return await self.mongo_logger.get_session_stats(self.session_id)

    async def get_session_calls(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all calls for current session from MongoDB.

        Returns:
            List of call documents or None if no logger
        """
        if not self.mongo_logger:
            return None

        return await self.mongo_logger.get_session_calls(self.session_id)