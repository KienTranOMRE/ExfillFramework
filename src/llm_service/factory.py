import os
from typing import Optional
from .base import LLMServiceBase
from .gemini_service import GeminiLLMService
from .qwen_service import QwenLLMService


class LLMServiceFactory:
    """
    Factory class for creating LLM service instances.
    """

    # Available LLM services
    SERVICES = {
        'gemini': GeminiLLMService,
        'qwen': QwenLLMService,
    }

    @classmethod
    def create(
        cls,
        service_name: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLMServiceBase:
        """
        Create an LLM service instance.

        Args:
            service_name: Name of the LLM service to use. If not provided,
                         will use LLM_SERVICE from environment, defaulting to 'gemini'.
                         Available services: 'gemini', 'qwen'
            model_name: Model to use. If not provided, uses service defaults.
            **kwargs: Additional service-specific parameters

        Returns:
            An instance of the requested LLM service

        Raises:
            ValueError: If the requested service is not supported or not configured
        """
        # Determine which service to use
        if service_name is None:
            service_name = os.getenv('LLM_SERVICE', 'gemini').lower()
        else:
            service_name = service_name.lower()

        # Check if service is supported
        if service_name not in cls.SERVICES:
            available = ', '.join(cls.SERVICES.keys())
            raise ValueError(
                f"Unsupported LLM service: '{service_name}'. "
                f"Available services: {available}"
            )

        # Get default model name from environment if not provided
        if model_name is None:
            env_var = f"{service_name.upper()}_MODEL"
            model_name = os.getenv(env_var)

        # Create the service instance
        service_class = cls.SERVICES[service_name]
        try:
            if model_name:
                service = service_class(model_name=model_name, **kwargs)
            else:
                service = service_class(**kwargs)
        except ImportError as e:
            raise ImportError(
                f"Failed to initialize {service_name} LLM service. "
                f"Missing dependencies: {str(e)}"
            )

        # Validate configuration
        if not service.validate_config():
            raise ValueError(
                f"{service.service_name} LLM service is not properly configured. "
                f"Please check your API key and configuration."
            )

        return service

    @classmethod
    def list_services(cls) -> list:
        """
        List all available LLM services.

        Returns:
            List of service names
        """
        return list(cls.SERVICES.keys())

    @classmethod
    def get_service_info(cls) -> dict:
        """
        Get information about available LLM services.

        Returns:
            Dictionary with service information
        """
        return {
            'gemini': {
                'name': 'Google Gemini',
                'env_vars': {
                    'GEMINI_API_KEY': 'API key for Gemini',
                    'GEMINI_MODEL': 'Model name (optional, default: gemini-3-flash-preview)'
                },
                'dependencies': ['google-generativeai'],
                'description': 'Google Gemini LLM with advanced reasoning capabilities',
                'default_model': 'gemini-3-flash-preview',
                'supported_models': [
                    'gemini-3-flash-preview',
                    'gemini-2.0-flash-exp',
                    'gemini-1.5-pro',
                    'gemini-1.5-flash'
                ]
            },
            'qwen': {
                'name': 'Qwen (OpenAI-compatible)',
                'env_vars': {
                    'QWEN_API_KEY': 'API key for Qwen service',
                    'QWEN_BASE_URL': 'Base URL for API endpoint',
                    'QWEN_MODEL': 'Model name (optional, default: qwen-turbo)'
                },
                'dependencies': ['openai'],
                'description': 'Qwen models via OpenAI-compatible API (Alibaba Cloud, local inference)',
                'default_model': 'qwen-turbo',
                'supported_models': [
                    'qwen-turbo',
                    'qwen-plus',
                    'qwen-max',
                    'qwen-2.5-72b-instruct',
                    'qwen-2.5-32b-instruct',
                    'qwen-2.5-14b-instruct'
                ],
                'example_urls': {
                    'Alibaba DashScope': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                    'Local vLLM': 'http://localhost:8000/v1',
                    'Local TGI': 'http://localhost:8080/v1'
                }
            }
        }
