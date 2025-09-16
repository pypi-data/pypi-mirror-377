"""
Simple MongoDB logger for Gemini API calls.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Dict, Any, Optional


class MongoLogger:
    """Simple MongoDB logger for individual API calls in parallel execution."""

    def __init__(self, mongodb_uri: str, database: str = "gemini_logs"):
        """
        Initialize MongoDB logger.

        Args:
            mongodb_uri: MongoDB connection URI
            database: Database name for logs (default: "gemini_logs")
        """
        self.client = AsyncIOMotorClient(mongodb_uri)
        self.db = self.client[database]
        self.calls = self.db.api_calls

    async def log_call(self, call_data: Dict[str, Any]) -> None:
        """
        Log individual API call to MongoDB.

        Args:
            call_data: Dictionary containing call information
                - session_id: Unique session identifier
                - request_id: Unique request identifier
                - status: "success" or "failed"
                - prompt: Input prompt/content
                - response: API response (if success)
                - error: Error message (if failed)
                - duration_ms: Call duration in milliseconds
                - model: Model name used
                - mode: Call mode (text/multimodal/structured)
        """
        document = {
            "session_id": call_data["session_id"],
            "request_id": call_data["request_id"],
            "status": call_data["status"],
            "prompt": call_data["prompt"],
            "duration_ms": call_data["duration_ms"],
            "timestamp": datetime.utcnow(),
            "model": call_data["model"],
            "mode": call_data.get("mode", "text")
        }

        # Add response or error based on status
        if call_data["status"] == "success":
            document["response"] = call_data.get("response")
            document["tokens_input"] = call_data.get("tokens_input")
            document["tokens_output"] = call_data.get("tokens_output")
        else:
            document["error"] = call_data.get("error")

        await self.calls.insert_one(document)

    async def get_session_calls(self, session_id: str) -> list:
        """
        Get all calls for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            List of call documents
        """
        cursor = self.calls.find({"session_id": session_id})
        return await cursor.to_list(length=None)

    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get basic statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session statistics
        """
        pipeline = [
            {"$match": {"session_id": session_id}},
            {"$group": {
                "_id": None,
                "total_calls": {"$sum": 1},
                "successful_calls": {
                    "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                },
                "failed_calls": {
                    "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                },
                "avg_duration": {"$avg": "$duration_ms"},
                "total_duration": {"$sum": "$duration_ms"},
                "total_tokens": {
                    "$sum": {"$add": [
                        {"$ifNull": ["$tokens_input", 0]},
                        {"$ifNull": ["$tokens_output", 0]}
                    ]}
                }
            }}
        ]

        result = await self.calls.aggregate(pipeline).to_list(1)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats

        return {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_duration": 0,
            "total_duration": 0,
            "total_tokens": 0
        }