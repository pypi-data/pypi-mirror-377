#!/usr/bin/env python3
"""
Multimodal parallel processing example with images and MongoDB logging.
"""

import asyncio
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from gemini_parallel import ParallelExecutor, ContentBuilder

# Load environment variables
load_dotenv()


def create_sample_images():
    """Create sample images for testing."""
    os.makedirs("temp_images", exist_ok=True)

    # Create simple colored rectangles as sample images
    colors = ["red", "blue", "green", "yellow"]
    image_paths = []

    for i, color in enumerate(colors):
        img = Image.new("RGB", (200, 200), color)
        draw = ImageDraw.Draw(img)
        draw.text((70, 90), f"Image {i+1}", fill="white")

        path = f"temp_images/sample_{color}.png"
        img.save(path)
        image_paths.append(path)

    return image_paths


async def main():
    """Multimodal parallel processing example."""

    # Create sample images
    print("Creating sample images...")
    image_paths = create_sample_images()

    # Create multimodal content
    contents = [
        ContentBuilder.with_image(image_paths[0], "What color is this image?"),
        ContentBuilder.with_image(image_paths[1], "Describe this image"),
        ContentBuilder.with_image(image_paths[2], "What do you see in this image?"),
        ContentBuilder.with_image(image_paths[3], "Analyze the contents of this image")
    ]

    # Initialize executor with MongoDB logging
    executor = ParallelExecutor(
        model="gemini-2.0-flash",
        max_concurrent=3,
        mongodb_uri=os.getenv("MONGODB_URI")
    )

    try:
        # Run parallel multimodal processing
        print("Processing images with prompts in parallel...")
        results = await executor.run_parallel(
            items=contents,
            mode="multimodal",
            show_progress=True
        )

        # Display results
        print("\n" + "="*60)
        print("MULTIMODAL RESULTS")
        print("="*60)

        for i, (content, result) in enumerate(zip(contents, results)):
            image_path = image_paths[i]
            prompt = content[-1]  # Last item is the prompt

            print(f"\n{i+1}. Image: {image_path}")
            print(f"   Prompt: {prompt}")
            print(f"   Status: {result['status']}")

            if result['status'] == 'success':
                print(f"   Response: {result['response']}")
                print(f"   Duration: {result['duration_ms']:.0f}ms")
            else:
                print(f"   Error: {result['error']}")

        # Show session statistics
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

            print(f"\nSession ID: {executor.session_id}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Clean up sample images
        import shutil
        if os.path.exists("temp_images"):
            shutil.rmtree("temp_images")
            print("\nCleaned up sample images")


if __name__ == "__main__":
    asyncio.run(main())