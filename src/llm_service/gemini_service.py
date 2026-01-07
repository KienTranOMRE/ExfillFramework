import os
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from .base import LLMServiceBase


class GeminiLLMService(LLMServiceBase):
    """
    LLM service implementation using Google Gemini API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3-flash-preview"
    ):
        """
        Initialize Gemini LLM service.

        Args:
            api_key: Gemini API key. If not provided, will use GEMINI_API_KEY from environment.
            model_name: Model to use (default: gemini-3-flash-preview)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._model_name = model_name

        if self.api_key:
            genai.configure(api_key=self.api_key)

    @property
    def service_name(self) -> str:
        return "Gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def validate_config(self) -> bool:
        """
        Validate that Gemini API key is configured.

        Returns:
            True if API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion using Gemini.

        Args:
            prompt: The user prompt/message
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system instruction
            **kwargs: Additional Gemini-specific parameters

        Returns:
            Generated text response

        Raises:
            ValueError: If API key is not configured
            Exception: If generation fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(
                f"{self.service_name} API key is not configured. "
                "Set GEMINI_API_KEY in environment."
            )

        # Prepare generation config
        generation_config = {
            "temperature": temperature,
        }

        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens

        # Add any additional kwargs
        generation_config.update(kwargs)

        # Initialize model
        model = genai.GenerativeModel(
            self._model_name,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None
        )

        # Generate response
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate response from conversation history using Gemini.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Roles: 'system', 'user', 'assistant'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini-specific parameters

        Returns:
            Generated response text

        Raises:
            ValueError: If API key is not configured or messages format is invalid
            Exception: If generation fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(
                f"{self.service_name} API key is not configured. "
                "Set GEMINI_API_KEY in environment."
            )

        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Extract system prompt if present
        system_prompt = None
        chat_messages = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                system_prompt = content
            elif role == "user":
                chat_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                chat_messages.append({"role": "model", "parts": [content]})
            else:
                raise ValueError(f"Unknown role: {role}. Must be 'system', 'user', or 'assistant'")

        # Prepare generation config
        generation_config = {
            "temperature": temperature,
        }

        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens

        generation_config.update(kwargs)

        # Initialize model
        model = genai.GenerativeModel(
            self._model_name,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None
        )

        try:
            # Start chat with history
            chat = model.start_chat(history=chat_messages[:-1] if len(chat_messages) > 1 else [])

            # Send the last message
            last_message = chat_messages[-1]["parts"][0] if chat_messages else ""
            response = chat.send_message(last_message)

            return response.text
        except Exception as e:
            raise Exception(f"Gemini chat failed: {str(e)}")
