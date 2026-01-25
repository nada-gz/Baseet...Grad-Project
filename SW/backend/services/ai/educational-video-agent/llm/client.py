"""Base Qwen API client."""
import asyncio
import os
from typing import Any
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError


BLOCKED_MODELS = ["qwen-plus", "qwen-turbo", "qwen-plus-character-ja"]


def validate_model(model_name: str) -> None:
    """Validate model is not blocked."""
    if model_name in BLOCKED_MODELS:
        raise ValueError(f"Model {model_name} is blocked. Use qwen-flash, qwen3-coder-flash, or qwen-max")


class QwenClient:
    """Async Qwen API client."""
    
    DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    DEFAULT_MODEL = "qwen-flash"
    MAX_RETRIES = 3
    
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise ValueError("QWEN_API_KEY not set")
        
        self.base_url = base_url or os.getenv("QWEN_BASE_URL", self.DEFAULT_BASE_URL)
        self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Make API call with retry logic."""
        validate_model(model)
        print(f"Using model: {model}")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                
                response = await self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response")
                return content.strip()
                
            except RateLimitError as e:
                last_error = e
                wait_time = 2 ** attempt
                print(f"  [Rate limited, retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s]")
                await asyncio.sleep(wait_time)
                
            except (APIConnectionError, APIError) as e:
                last_error = e
                wait_time = 2 ** attempt
                print(f"  [API error, retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s]")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    print(f"  [Error, retry {attempt + 1}/{self.MAX_RETRIES} in {wait_time}s]")
                    await asyncio.sleep(wait_time)
        
        raise RuntimeError(f"API call failed after {self.MAX_RETRIES} attempts: {last_error}")
