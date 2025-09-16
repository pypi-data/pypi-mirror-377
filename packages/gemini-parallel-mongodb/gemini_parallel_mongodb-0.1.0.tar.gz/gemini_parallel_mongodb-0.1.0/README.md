# Gemini Parallel

A Python package for running Gemini API calls in parallel with MongoDB logging support. Supports text, multimodal (images), and structured output processing.

## Features

- **Parallel Processing**: Execute multiple Gemini API calls concurrently with configurable limits
- **MongoDB Logging**: Log each individual API call to MongoDB for tracking and analysis
- **Multiple Modes**: Support for text, multimodal (with images), and structured output
- **Rate Limiting**: Built-in rate limiting and retry logic
- **Progress Tracking**: Visual progress bars with tqdm
- **Flexible Content**: Support for various image formats and Pydantic models

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Dependencies

- `google-genai` - Official Google GenAI Python SDK
- `motor` - Async MongoDB driver
- `pydantic` - Data validation and parsing
- `tqdm` - Progress bars
- `python-dotenv` - Environment variable management
- `pillow` - Image processing
- `pymongo` - MongoDB driver

## Setup

1. **Environment Variables**: Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Connection URI
MONGODB_URI=mongodb://localhost:27017
```

2. **MongoDB**: Make sure MongoDB is running and accessible via the URI in your `.env` file.

## Quick Start

### Basic Text Processing

```python
import asyncio
import os
from dotenv import load_dotenv
from gemini_parallel import ParallelExecutor

load_dotenv()

async def main():
    executor = ParallelExecutor(
        model="gemini-2.0-flash",
        max_concurrent=50,
        mongodb_uri=os.getenv("MONGODB_URI")
    )

    prompts = [
        "Explain AI in simple terms",
        "What is machine learning?",
        "Define deep learning"
    ]

    results = await executor.run_parallel(
        items=prompts,
        mode="text"
    )

    for result in results:
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Response: {result['response']}")

asyncio.run(main())
```

### Multimodal with Images

```python
from gemini_parallel import ParallelExecutor, ContentBuilder

# Create content with images
contents = [
    ContentBuilder.with_image("image1.jpg", "Describe this image"),
    ContentBuilder.with_image("image2.jpg", "What's in this photo?"),
    ContentBuilder.with_images(["img1.jpg", "img2.jpg"], "Compare these images")
]

executor = ParallelExecutor(mongodb_uri=os.getenv("MONGODB_URI"))

results = await executor.run_parallel(
    items=contents,
    mode="multimodal"
)
```

### Structured Output with Pydantic

```python
from pydantic import BaseModel
from typing import List

class Analysis(BaseModel):
    sentiment: str
    confidence: float
    keywords: List[str]

executor = ParallelExecutor(mongodb_uri=os.getenv("MONGODB_URI"))

results = await executor.run_parallel(
    items=["Great product!", "Terrible service"],
    mode="structured",
    response_schema=Analysis
)
```

## MongoDB Logging

Each API call is logged to MongoDB with the following structure:

```json
{
  "_id": ObjectId,
  "session_id": "uuid-string",
  "request_id": "req_0",
  "status": "success|failed",
  "prompt": "...",
  "response": "...",
  "error": "...",
  "duration_ms": 1234.5,
  "timestamp": ISODate,
  "model": "gemini-2.0-flash",
  "mode": "text|multimodal|structured",
  "tokens_input": 100,
  "tokens_output": 200
}
```

### Querying Logs

```python
# Get session statistics
stats = await executor.get_session_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Success rate: {stats['successful_calls']/stats['total_calls']*100:.1f}%")

# Get all calls for session
calls = await executor.get_session_calls()
for call in calls:
    print(f"{call['request_id']}: {call['status']} - {call['duration_ms']}ms")
```

## Configuration Options

### ParallelExecutor Parameters

- `model`: Gemini model to use (default: "gemini-2.0-flash")
- `max_concurrent`: Maximum concurrent requests (default: 50)
- `request_delay`: Delay between requests in seconds (default: 0.02)
- `max_retries`: Maximum retry attempts (default: 3)
- `mongodb_uri`: MongoDB connection URI (optional)
- `api_key`: Gemini API key (defaults to GEMINI_API_KEY env var)

### Rate Limiting Guidelines

For Gemini 2.5 Flash:

- **Free Tier**: `max_concurrent=2-5`, `request_delay=1.0`
- **Paid Tier 1**: `max_concurrent=50`, `request_delay=0.02` (targets ~3000 RPM)
- **Paid Tier 2**: `max_concurrent=100`, `request_delay=0.01`

## Examples

Run the provided examples:

```bash
# Basic text processing
python examples/basic_parallel.py

# Multimodal with images
python examples/with_images.py

# Structured output
python examples/structured_output.py
```

## Error Handling

The package includes robust error handling:

- **Automatic retries** with exponential backoff
- **Rate limiting** to avoid API limits
- **Individual call logging** for debugging
- **Graceful failure** handling

## Session Management

Each executor creates a unique session ID that groups related calls:

```python
executor = ParallelExecutor(mongodb_uri=uri)
print(f"Session ID: {executor.session_id}")

# All calls in this session will be tagged with this ID
results = await executor.run_parallel(items)

# Query MongoDB for this session's calls
db.api_calls.find({"session_id": executor.session_id})
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.