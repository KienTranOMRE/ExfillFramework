import os
from typing import Optional
from .base import OCRServiceBase
from .gemini_service import GeminiOCRService
from .chandra_service import ChandraOCRService


class OCRServiceFactory:
    """
    Factory class for creating OCR service instances.
    """

    # Available OCR services
    SERVICES = {
        'gemini': GeminiOCRService,
        'chandra': ChandraOCRService,
    }

    @classmethod
    def create(cls, service_name: Optional[str] = None) -> OCRServiceBase:
        """
        Create an OCR service instance.

        Args:
            service_name: Name of the OCR service to use. If not provided,
                         will use OCR_SERVICE from environment, defaulting to 'gemini'.
                         Available services: 'gemini', 'chandra'

        Returns:
            An instance of the requested OCR service

        Raises:
            ValueError: If the requested service is not supported or not configured
        """
        # Determine which service to use
        if service_name is None:
            service_name = os.getenv('OCR_SERVICE', 'gemini').lower()
        else:
            service_name = service_name.lower()

        # Check if service is supported
        if service_name not in cls.SERVICES:
            available = ', '.join(cls.SERVICES.keys())
            raise ValueError(
                f"Unsupported OCR service: '{service_name}'. "
                f"Available services: {available}"
            )

        # Create the service instance
        service_class = cls.SERVICES[service_name]
        try:
            service = service_class()
        except ImportError as e:
            raise ImportError(
                f"Failed to initialize {service_name} OCR service. "
                f"Missing dependencies: {str(e)}"
            )

        # Validate configuration
        if not service.validate_config():
            raise ValueError(
                f"{service.service_name} OCR service is not properly configured. "
                f"Please check your API key configuration."
            )

        return service

    @classmethod
    def list_services(cls) -> list:
        """
        List all available OCR services.

        Returns:
            List of service names
        """
        return list(cls.SERVICES.keys())

    @classmethod
    def get_service_info(cls) -> dict:
        """
        Get information about available OCR services.

        Returns:
            Dictionary with service information
        """
        return {
            'gemini': {
                'name': 'Google Gemini',
                'env_var': 'GEMINI_API_KEY',
                'dependencies': ['google-generativeai'],
                'description': 'Google Gemini API with advanced vision capabilities'
            },
            'chandra': {
                'name': 'Chandra OCR',
                'env_var': 'CHANDRA_API_URL',
                'dependencies': ['requests'],
                'description': 'Chandra OCR API service (default: http://localhost:8000)'
            }
        }
