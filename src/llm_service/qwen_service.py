import os
from typing import Optional, List, Dict, Any
from openai import OpenAI
from .base import LLMServiceBase


class QwenLLMService(LLMServiceBase):
    """
    LLM service implementation for Qwen using OpenAI-compatible API.

    This client works with any OpenAI-compatible API endpoint, including:
    - Qwen models hosted on compatible platforms
    - Local inference servers (vLLM, Text Generation Inference)
    - Cloud providers with OpenAI-compatible APIs
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "qwen-turbo"
    ):
        """
        Initialize Qwen LLM service with OpenAI-compatible API.

        Args:
            api_key: API key for the service. If not provided, uses QWEN_API_KEY from environment.
            base_url: Base URL for the API endpoint. If not provided, uses QWEN_BASE_URL from environment.
                     Example: "https://dashscope.aliyuncs.com/compatible-mode/v1"
                     or "http://localhost:8000/v1" for local inference
            model_name: Model identifier (default: qwen-turbo)
                       Common options: qwen-turbo, qwen-plus, qwen-max, qwen-2.5-72b-instruct
        """
        self.api_key = api_key or os.getenv("QWEN_API_KEY", "EMPTY")
        self.base_url = base_url or os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self._model_name = model_name

        # Initialize OpenAI client with custom endpoint
        if self.api_key and self.base_url:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None

    @property
    def service_name(self) -> str:
        return "Qwen"

    @property
    def model_name(self) -> str:
        return self._model_name

    def validate_config(self) -> bool:
        """
        Validate that API key and base URL are configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        return (
            self.api_key is not None and len(self.api_key) > 0 and
            self.base_url is not None and len(self.base_url) > 0 and
            self.client is not None
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion using Qwen via OpenAI-compatible API.

        Args:
            prompt: The user prompt/message
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system instruction
            **kwargs: Additional API parameters (top_p, frequency_penalty, etc.)

        Returns:
            Generated text response

        Raises:
            ValueError: If API is not configured
            Exception: If generation fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(
                f"{self.service_name} is not properly configured. "
                "Set QWEN_API_KEY and QWEN_BASE_URL in environment."
            )

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare API call parameters
        api_params = {
            "model": self._model_name,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            api_params["max_tokens"] = max_tokens

        # Add any additional kwargs
        api_params.update(kwargs)

        try:
            # Call API
            response = self.client.chat.completions.create(**api_params)

            # Extract response text
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Qwen generation failed: {str(e)}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate response from conversation history using Qwen.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Roles: 'system', 'user', 'assistant'
                     Example: [
                         {"role": "system", "content": "You are helpful"},
                         {"role": "user", "content": "Hello"},
                         {"role": "assistant", "content": "Hi!"},
                         {"role": "user", "content": "How are you?"}
                     ]
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional API parameters

        Returns:
            Generated response text

        Raises:
            ValueError: If API is not configured or messages format is invalid
            Exception: If generation fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(
                f"{self.service_name} is not properly configured. "
                "Set QWEN_API_KEY and QWEN_BASE_URL in environment."
            )

        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Validate message format
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise ValueError("Each message must have 'role' and 'content' keys")

            role = msg["role"]
            if role not in ["system", "user", "assistant"]:
                raise ValueError(
                    f"Invalid role: {role}. Must be 'system', 'user', or 'assistant'"
                )

        # Prepare API call parameters
        api_params = {
            "model": self._model_name,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            api_params["max_tokens"] = max_tokens

        # Add any additional kwargs
        api_params.update(kwargs)

        try:
            # Call API
            response = self.client.chat.completions.create(**api_params)

            # Extract response text
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Qwen chat failed: {str(e)}")

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Stream response from conversation history (yields chunks).

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional API parameters

        Yields:
            Response text chunks

        Raises:
            ValueError: If API is not configured
            Exception: If streaming fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(
                f"{self.service_name} is not properly configured. "
                "Set QWEN_API_KEY and QWEN_BASE_URL in environment."
            )

        # Prepare API call parameters
        api_params = {
            "model": self._model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            api_params["max_tokens"] = max_tokens

        api_params.update(kwargs)

        try:
            # Call streaming API
            stream = self.client.chat.completions.create(**api_params)

            # Yield chunks
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Qwen streaming failed: {str(e)}")
