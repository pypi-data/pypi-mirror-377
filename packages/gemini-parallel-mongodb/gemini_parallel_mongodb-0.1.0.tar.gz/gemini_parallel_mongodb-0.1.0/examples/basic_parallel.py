#!/usr/bin/env python3
"""
Basic parallel text processing example with MongoDB logging.
"""

import asyncio
import os
from dotenv import load_dotenv
from gemini_parallel import ParallelExecutor

# Load environment variables
load_dotenv()


async def main():
    """Basic parallel text processing example."""

    # Sample prompts
    prompts = [
        "Explain artificial intelligence in simple terms",
        "What is machine learning?",
        "Define deep learning",
        "How do neural networks work?",
        "What is natural language processing?",
        "Explain computer vision",
        "What is reinforcement learning?",
        "Define generative AI"
    ]

    # Initialize executor with MongoDB logging
    executor = ParallelExecutor(
        model="gemini-2.0-flash",
        max_concurrent=4,  # Conservative for free tier
        mongodb_uri=os.getenv("MONGODB_URI")
    )

    try:
        # Run parallel text processing
        print("Processing prompts in parallel...")
        results = await executor.run_parallel(
            items=prompts,
            mode="text",
            show_progress=True
        )

        # Display results
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)

        for i, (prompt, result) in enumerate(zip(prompts, results)):
            print(f"\n{i+1}. {prompt}")
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print(f"   Response: {result['response'][:100]}...")
                print(f"   Duration: {result['duration_ms']:.0f}ms")
            else:
                print(f"   Error: {result['error']}")

        # Show session statistics if MongoDB logging is enabled
        if executor.mongo_logger:
            print("\n" + "="*60)
            print("SESSION STATISTICS")
            print("="*60)

            stats = await executor.get_session_stats()
            if stats:
                print(f"Total calls: {stats['total_calls']}")
                print(f"Successful: {stats['successful_calls']}")
                print(f"Failed: {stats['failed_calls']}")
                print(f"Average duration: {stats['avg_duration']:.1f}ms")
                print(f"Total tokens: {stats['total_tokens']}")

            print(f"\nSession ID: {executor.session_id}")
            print("Check MongoDB collection 'gemini_logs.api_calls' for detailed logs")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())