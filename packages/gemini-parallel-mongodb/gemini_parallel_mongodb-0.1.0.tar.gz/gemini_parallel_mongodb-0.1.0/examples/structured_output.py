#!/usr/bin/env python3
"""
Structured output parallel processing example with Pydantic models and MongoDB logging.
"""

import asyncio
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from gemini_parallel import ParallelExecutor

# Load environment variables
load_dotenv()


class SentimentAnalysis(BaseModel):
    """Pydantic model for sentiment analysis results."""
    text: str
    sentiment: str  # positive, negative, neutral
    confidence: float  # 0.0 to 1.0
    emotions: List[str]  # list of detected emotions
    summary: str


class ProductReview(BaseModel):
    """Pydantic model for product review analysis."""
    review_text: str
    rating: int  # 1-5 stars
    pros: List[str]
    cons: List[str]
    recommendation: str
    category: str


async def sentiment_analysis_example():
    """Example of structured sentiment analysis."""
    print("="*60)
    print("SENTIMENT ANALYSIS EXAMPLE")
    print("="*60)

    # Sample texts for sentiment analysis
    texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is the worst purchase I've ever made. Complete waste of money.",
        "It's okay, nothing special but does what it's supposed to do.",
        "Outstanding quality and excellent customer service. Highly recommended!",
        "Not bad, but could be improved in several areas.",
        "Terrible experience. Product broke after one day."
    ]

    executor = ParallelExecutor(
        model="gemini-2.0-flash",
        max_concurrent=3,
        mongodb_uri=os.getenv("MONGODB_URI")
    )

    # Create prompts for sentiment analysis
    prompts = [
        f"Analyze the sentiment of this text: '{text}'"
        for text in texts
    ]

    try:
        results = await executor.run_parallel(
            items=prompts,
            mode="structured",
            response_schema=SentimentAnalysis,
            show_progress=True
        )

        # Display results
        for i, result in enumerate(results):
            print(f"\n{i+1}. Text: {texts[i]}")
            print(f"   Status: {result['status']}")

            if result['status'] == 'success':
                try:
                    # Parse JSON response
                    import json
                    analysis = json.loads(result['response'])
                    print(f"   Sentiment: {analysis.get('sentiment', 'N/A')}")
                    print(f"   Confidence: {analysis.get('confidence', 'N/A')}")
                    print(f"   Emotions: {analysis.get('emotions', [])}")
                    print(f"   Summary: {analysis.get('summary', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"   Raw response: {result['response']}")
            else:
                print(f"   Error: {result['error']}")

        return executor.session_id

    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return None


async def product_review_example():
    """Example of structured product review analysis."""
    print("\n" + "="*60)
    print("PRODUCT REVIEW ANALYSIS EXAMPLE")
    print("="*60)

    # Sample product reviews
    reviews = [
        "This laptop is fantastic! Great performance, beautiful display, and long battery life. The only downside is it's a bit heavy for travel.",
        "Coffee maker broke after 2 months. Poor build quality and terrible customer support. Don't waste your money.",
        "Decent headphones for the price. Good sound quality but the build feels cheap. Comfortable for short sessions.",
        "Best smartphone I've ever owned! Camera is incredible, battery lasts all day, and the design is sleek. Worth every penny."
    ]

    executor = ParallelExecutor(
        model="gemini-2.0-flash",
        max_concurrent=2,
        mongodb_uri=os.getenv("MONGODB_URI")
    )

    # Create prompts for product review analysis
    prompts = [
        f"Analyze this product review and extract structured information: '{review}'"
        for review in reviews
    ]

    try:
        results = await executor.run_parallel(
            items=prompts,
            mode="structured",
            response_schema=ProductReview,
            show_progress=True
        )

        # Display results
        for i, result in enumerate(results):
            print(f"\n{i+1}. Review: {reviews[i]}")
            print(f"   Status: {result['status']}")

            if result['status'] == 'success':
                try:
                    import json
                    analysis = json.loads(result['response'])
                    print(f"   Rating: {analysis.get('rating', 'N/A')}/5 stars")
                    print(f"   Pros: {analysis.get('pros', [])}")
                    print(f"   Cons: {analysis.get('cons', [])}")
                    print(f"   Category: {analysis.get('category', 'N/A')}")
                    print(f"   Recommendation: {analysis.get('recommendation', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"   Raw response: {result['response']}")
            else:
                print(f"   Error: {result['error']}")

        return executor.session_id

    except Exception as e:
        print(f"Error in product review analysis: {e}")
        return None


async def main():
    """Run structured output examples."""

    session_ids = []

    # Run sentiment analysis example
    session_id = await sentiment_analysis_example()
    if session_id:
        session_ids.append(session_id)

    # Run product review example
    session_id = await product_review_example()
    if session_id:
        session_ids.append(session_id)

    # Show MongoDB session information
    if session_ids and os.getenv("MONGODB_URI"):
        print("\n" + "="*60)
        print("MONGODB SESSION INFORMATION")
        print("="*60)

        for i, session_id in enumerate(session_ids):
            print(f"Session {i+1}: {session_id}")

        print("\nCheck MongoDB collection 'gemini_logs.api_calls' for detailed structured output logs")


if __name__ == "__main__":
    asyncio.run(main())