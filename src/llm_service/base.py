from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class LLMServiceBase(ABC):
    """
    Abstract base class for LLM services.
    All LLM service implementations must inherit from this class.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion from a prompt.

        Args:
            prompt: The user prompt/message
            temperature: Sampling temperature (0.0 to 2.0). Higher values = more random
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system message/instruction
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate response from a conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [
                         {"role": "system", "content": "You are a helpful assistant"},
                         {"role": "user", "content": "Hello!"},
                         {"role": "assistant", "content": "Hi! How can I help?"},
                         {"role": "user", "content": "What's the weather?"}
                     ]
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated response text

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the service is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """
        Get the name of the LLM service.

        Returns:
            Name of the service
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the model identifier/name.

        Returns:
            Model name or identifier
        """
        pass
