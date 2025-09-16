#!/usr/bin/env python3
"""
Parallel Example: Async Gemini API Usage
Demonstrates how to use async non-streaming API calls with concurrency control.
Based on patterns from evaluator.py.
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Tuple
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from tqdm.asyncio import tqdm

# Load environment variables
load_dotenv()


class AsyncMeetingAnalyzer:
    """
    Example async meeting analyzer using non-streaming Gemini API.
    
    Rate Limits for Gemini 2.5 Flash-Lite Tier 1 (Paid):
    - 4,000 RPM (requests per minute) = 66.67 requests per second max
    - 4,000,000 TPM (tokens per minute) = 66,667 tokens per second max
    
    Default settings target ~3,000 RPM (75% of limit) for safety margin.
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash-lite",
        max_concurrent: int = 50,  # Tier 1: 4,000 RPM allows ~66 RPS, use 50 for safety
        request_delay: float = 0.02,  # 20ms delay for ~3,000 RPM (75% of 4,000 RPM limit)
        max_retries: int = 3
    ):
        """
        Initialize async analyzer.
        
        Args:
            model: Gemini model to use
            max_concurrent: Maximum concurrent API requests
            request_delay: Delay between requests (seconds)
            max_retries: Maximum retry attempts
        """
        self.model = model
        self.max_concurrent = max_concurrent
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.client = None
        
    async def setup_client(self) -> None:
        """Initialize the Gemini client."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        
        self.client = genai.Client(api_key=api_key)
        print(f"✅ Gemini client initialized with model: {self.model}")
    
    def create_analysis_prompt(self, summary: str, description: str) -> str:
        """Create prompt for meeting analysis."""
        return f"""다음 캘린더 이벤트를 분석해주세요:

Summary: {summary}
Description: {description}

다음을 판단해주세요:
1. 이것이 비즈니스 미팅인가요? (회사 업무, 사업 관련 만남, 고객 미팅, 투자 관련, 채용 면접 등)
2. 텍스트에서 사람 이름을 모두 추출해주세요 (한국어 이름, 영어 이름 모두 포함)

사람 이름만 추출하고, 회사명이나 직책은 제외해주세요.

JSON 형태로만 응답해주세요:
{{
  "is_business_meeting": true/false,
  "peoples": ["이름1", "이름2", ...]
}}"""

    async def analyze_single_meeting(
        self,
        meeting_data: Dict[str, str],
        semaphore: asyncio.Semaphore,
        meeting_id: int
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Analyze a single meeting asynchronously.
        
        Args:
            meeting_data: Dict with 'summary' and 'description'
            semaphore: Concurrency control
            meeting_id: Meeting identifier for tracking
            
        Returns:
            Tuple of (meeting_id, analysis_result)
        """
        async with semaphore:
            start_time = time.time()
            
            # Rate limiting
            await asyncio.sleep(self.request_delay)
            
            summary = meeting_data.get('summary', '')
            description = meeting_data.get('description', '')
            
            # Skip empty meetings
            if not summary and not description:
                return meeting_id, {
                    'is_business_meeting': False,
                    'peoples': [],
                    'analysis_time': 0.0,
                    'error': None
                }
            
            prompt = self.create_analysis_prompt(summary, description)
            
            # Retry logic
            for attempt in range(self.max_retries):
                try:
                    # 🔥 KEY: Non-streaming async API call
                    response = await self.client.aio.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=0),
                            response_mime_type="application/json",
                            response_schema=genai.types.Schema(
                                type=genai.types.Type.OBJECT,
                                required=["peoples", "is_business_meeting"],
                                properties={
                                    "peoples": genai.types.Schema(
                                        type=genai.types.Type.ARRAY,
                                        items=genai.types.Schema(
                                            type=genai.types.Type.STRING,
                                        ),
                                    ),
                                    "is_business_meeting": genai.types.Schema(
                                        type=genai.types.Type.BOOLEAN,
                                    ),
                                },
                            ),
                            temperature=0.1,
                        ),
                    )
                    
                    if not response.text:
                        if attempt == self.max_retries - 1:
                            return meeting_id, {
                                'is_business_meeting': False,
                                'peoples': [],
                                'analysis_time': time.time() - start_time,
                                'error': 'Empty API response'
                            }
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    # Parse JSON response
                    result = json.loads(response.text.strip())
                    
                    return meeting_id, {
                        'is_business_meeting': result.get('is_business_meeting', False),
                        'peoples': result.get('peoples', []),
                        'analysis_time': time.time() - start_time,
                        'error': None
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error for meeting {meeting_id} on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries - 1:
                        return meeting_id, {
                            'is_business_meeting': False,
                            'peoples': [],
                            'analysis_time': time.time() - start_time,
                            'error': f'JSON decode error: {str(e)}'
                        }
                    await asyncio.sleep(2 ** attempt)
                    
                except Exception as e:
                    print(f"⚠️ API error for meeting {meeting_id} on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries - 1:
                        return meeting_id, {
                            'is_business_meeting': False,
                            'peoples': [],
                            'analysis_time': time.time() - start_time,
                            'error': str(e)
                        }
                    await asyncio.sleep(2 ** attempt)
    
    async def analyze_meetings_parallel(
        self,
        meetings: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple meetings in parallel.
        
        Args:
            meetings: List of meeting data dicts
            
        Returns:
            List of analysis results in original order
        """
        if not self.client:
            await self.setup_client()
        
        print(f"🚀 Starting parallel analysis of {len(meetings)} meetings")
        print(f"📊 Max concurrent requests: {self.max_concurrent}")
        print(f"⏱️ Request delay: {self.request_delay}s")
        print(f"🎯 Target rate: ~{60 / max(self.request_delay * self.max_concurrent, 0.001):.0f} requests/minute")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create tasks for all meetings
        tasks = []
        for i, meeting in enumerate(meetings):
            task = self.analyze_single_meeting(meeting, semaphore, i)
            tasks.append(task)
        
        start_time = time.time()
        
        # 🔥 KEY: Execute all tasks in parallel with progress bar
        results = await tqdm.gather(
            *tasks, 
            desc="🧠 Processing meetings",
            ncols=120,
            unit=" meetings",
            colour="green",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        total_time = time.time() - start_time
        
        # Process results and maintain original order
        analysis_results = [None] * len(meetings)
        successful_analyses = 0
        failed_analyses = 0
        
        for result in results:
            if isinstance(result, Exception):
                print(f"❌ Task failed: {result}")
                failed_analyses += 1
                continue
                
            meeting_id, analysis = result
            analysis_results[meeting_id] = analysis
            
            if analysis['error']:
                failed_analyses += 1
            else:
                successful_analyses += 1
        
        # Fill any None results with default values
        for i in range(len(analysis_results)):
            if analysis_results[i] is None:
                analysis_results[i] = {
                    'is_business_meeting': False,
                    'peoples': [],
                    'analysis_time': 0.0,
                    'error': 'Task failed'
                }
        
        # Print statistics
        print("✅ Analysis completed!")
        print(f"📈 Total time: {total_time:.2f}s")
        print(f"📊 Successful: {successful_analyses}")
        print(f"❌ Failed: {failed_analyses}")
        print(f"⚡ Average time per meeting: {total_time / len(meetings):.3f}s")
        print(f"🚀 Requests per second: {len(meetings) / total_time:.2f}")
        
        return analysis_results


async def main():
    """Example usage of async meeting analyzer."""
    
    # Sample meeting data
    sample_meetings = [
        {
            'summary': '스트리미 김경돈 미팅',
            'description': '서울특별시 강남구 영동대로 704, 삼강빌딩 7층010-2205-6712'
        },
        {
            'summary': '신동일 미팅',
            'description': '서울대 경영서울대 로스쿨2019년부터 세종에서 근무'
        },
        {
            'summary': '조민 크래프트테크놀로지스 이사 미팅',
            'description': '아젠다: 조민 이사는 암호 화폐 선물 거래를 위한 인프라를 원하고...'
        },
        {
            'summary': '은행 업무 처리',
            'description': '수표 입금'
        },
        {
            'summary': '진에어 특가 예약',
            'description': ''
        }
    ]
    
    # Initialize analyzer with Tier 1 paid settings
    analyzer = AsyncMeetingAnalyzer(
        max_concurrent=50,  # Tier 1: optimized for 4,000 RPM limit
        request_delay=0.02  # 20ms delay for ~3,000 RPM (safe margin)
    )
    
    try:
        # Analyze meetings in parallel
        results = await analyzer.analyze_meetings_parallel(sample_meetings)
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        for i, (meeting, result) in enumerate(zip(sample_meetings, results)):
            print(f"\n{i+1}. {meeting['summary']}")
            print(f"   Business Meeting: {result['is_business_meeting']}")
            print(f"   People: {result['peoples']}")
            print(f"   Analysis Time: {result['analysis_time']:.3f}s")
            if result['error']:
                print(f"   Error: {result['error']}")
                
    except Exception as e:
        print(f"❌ Error running analysis: {e}")


if __name__ == '__main__':
    # Run the async example
    asyncio.run(main())