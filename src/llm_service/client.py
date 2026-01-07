"""
High-level LLM client providing convenient functions for common operations.
"""

import os
from typing import Optional, List, Dict
from .factory import LLMServiceFactory


def generate(
    prompt: str,
    service: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    Generate text completion using the configured LLM service.

    Args:
        prompt: The user prompt/message
        service: LLM service to use ('gemini' or 'qwen').
                If not provided, uses LLM_SERVICE from environment (default: 'gemini')
        model: Model to use. If not provided, uses service defaults.
        temperature: Sampling temperature (0.0 to 2.0). Higher = more random.
        max_tokens: Maximum number of tokens to generate
        system_prompt: Optional system message/instruction
        **kwargs: Additional provider-specific parameters

    Returns:
        Generated text response

    Raises:
        ValueError: If the service is not supported or not configured
        Exception: If generation fails

    Example:
        >>> # Use default Gemini
        >>> response = generate("Explain quantum computing in simple terms")

        >>> # Use Qwen with system prompt
        >>> response = generate(
        ...     "What is AI?",
        ...     service="qwen",
        ...     system_prompt="You are a helpful AI assistant"
        ... )
    """
    # Create LLM service instance
    llm_service = LLMServiceFactory.create(service, model)

    # Generate response
    return llm_service.generate(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        **kwargs
    )


def chat(
    messages: List[Dict[str, str]],
    service: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str:
    """
    Generate response from a conversation history.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
                 Example: [
                     {"role": "system", "content": "You are helpful"},
                     {"role": "user", "content": "Hello!"},
                     {"role": "assistant", "content": "Hi! How can I help?"},
                     {"role": "user", "content": "Tell me a joke"}
                 ]
        service: LLM service to use ('gemini' or 'qwen')
        model: Model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional provider-specific parameters

    Returns:
        Generated response text

    Raises:
        ValueError: If the service is not supported or messages format is invalid
        Exception: If generation fails

    Example:
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant"},
        ...     {"role": "user", "content": "What's 2+2?"},
        ... ]
        >>> response = chat(messages, service="gemini")
    """
    # Create LLM service instance
    llm_service = LLMServiceFactory.create(service, model)

    # Generate response
    return llm_service.chat(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def list_available_services():
    """
    Print information about available LLM services.

    Example:
        >>> list_available_services()
        Available LLM Services:
        ============================================================

        GEMINI: Google Gemini
          Environment Variables:
            - GEMINI_API_KEY: API key for Gemini
            - GEMINI_MODEL: Model name (optional)
          Dependencies: google-generativeai
          Description: Google Gemini LLM with advanced reasoning capabilities
          Default Model: gemini-3-flash-preview
        ...
    """
    services = LLMServiceFactory.get_service_info()

    print("Available LLM Services:")
    print("=" * 60)

    for service_key, info in services.items():
        print(f"\n{service_key.upper()}: {info['name']}")
        print(f"  Environment Variables:")
        for env_var, description in info['env_vars'].items():
            print(f"    - {env_var}: {description}")
        print(f"  Dependencies: {', '.join(info['dependencies'])}")
        print(f"  Description: {info['description']}")
        print(f"  Default Model: {info['default_model']}")

        if 'example_urls' in info:
            print(f"  Example Base URLs:")
            for platform, url in info['example_urls'].items():
                print(f"    - {platform}: {url}")

    print("\n" + "=" * 60)
    print("\nTo use a service, set LLM_SERVICE environment variable")
    print("Examples:")
    print("  LLM_SERVICE=gemini")
    print("  LLM_SERVICE=qwen")


class LLMClient:
    """
    High-level LLM client class for maintaining conversation state.

    Example:
        >>> # Create a client
        >>> client = LLMClient(service="gemini", system_prompt="You are helpful")

        >>> # Have a conversation
        >>> response1 = client.send("Hello!")
        >>> response2 = client.send("Tell me about Python")

        >>> # Get conversation history
        >>> history = client.get_history()

        >>> # Clear history
        >>> client.clear_history()
    """

    def __init__(
        self,
        service: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize LLM client.

        Args:
            service: LLM service to use
            model: Model to use
            system_prompt: System instruction for the conversation
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
        """
        self.llm_service = LLMServiceFactory.create(service, model)
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history: List[Dict[str, str]] = []

        # Add system prompt to history if provided
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })

    def send(self, message: str, **kwargs) -> str:
        """
        Send a message and get a response.

        Args:
            message: User message
            **kwargs: Additional parameters for this request

        Returns:
            Assistant's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Generate response
        response = self.llm_service.chat(
            messages=self.conversation_history,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            List of message dicts
        """
        return self.conversation_history.copy()

    def clear_history(self, keep_system_prompt: bool = True):
        """
        Clear conversation history.

        Args:
            keep_system_prompt: If True, keeps the system prompt in history
        """
        if keep_system_prompt and self.system_prompt:
            self.conversation_history = [{
                "role": "system",
                "content": self.system_prompt
            }]
        else:
            self.conversation_history = []

    def set_system_prompt(self, system_prompt: str):
        """
        Update the system prompt.

        Args:
            system_prompt: New system prompt
        """
        self.system_prompt = system_prompt

        # Update in history
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = system_prompt
        else:
            self.conversation_history.insert(0, {
                "role": "system",
                "content": system_prompt
            })


if __name__ == "__main__":
    # Show available services
    list_available_services()
