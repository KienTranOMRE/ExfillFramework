from abc import ABC, abstractmethod
from typing import Optional


class OCRServiceBase(ABC):
    """
    Abstract base class for OCR services.
    All OCR service implementations must inherit from this class.
    """

    @abstractmethod
    def ocr(self, pdf_file_path: str) -> str:
        """
        Perform OCR on a PDF file.

        Args:
            pdf_file_path: Path to the PDF file

        Returns:
            Extracted text in markdown format

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If OCR processing fails
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
        Get the name of the OCR service.

        Returns:
            Name of the service
        """
        pass
