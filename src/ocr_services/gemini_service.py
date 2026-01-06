import os
import google.generativeai as genai
from .base import OCRServiceBase


class GeminiOCRService(OCRServiceBase):
    """
    OCR service implementation using Google Gemini API.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Gemini OCR service.

        Args:
            api_key: Gemini API key. If not provided, will use GEMINI_API_KEY from environment.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    @property
    def service_name(self) -> str:
        return "Gemini"

    def validate_config(self) -> bool:
        """
        Validate that Gemini API key is configured.

        Returns:
            True if API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0

    def ocr(self, pdf_file_path: str) -> str:
        """
        Perform OCR on a PDF file using Gemini API.

        Args:
            pdf_file_path: Path to the PDF file

        Returns:
            Extracted text in markdown format

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If API key is not configured
            Exception: If OCR processing fails
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError(f"{self.service_name} API key is not configured. Set GEMINI_API_KEY in environment.")

        # Validate file exists
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")

        # Upload the PDF file to Gemini
        pdf_file = genai.upload_file(pdf_file_path)

        # Initialize the model (using Gemini 3 Flash)
        model = genai.GenerativeModel("gemini-3-flash-preview")

        # Create prompt for OCR
        prompt = """Extract all text from this PDF document and format it in markdown.
    Preserve the structure, headings, lists, tables, and formatting as much as possible.
    Return only the extracted text in clean markdown format."""

        # Generate content
        response = model.generate_content([pdf_file, prompt])

        return response.text
